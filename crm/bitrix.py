"""Работа с Bitrix24 через входящий вебхук (REST). Используются только стандартные поля CRM."""
import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

log = logging.getLogger(__name__)


class BitrixError(Exception):
    pass


def is_configured():
    return bool(settings.BITRIX24_WEBHOOK_URL)


def call(method, params=None):
    if not is_configured():
        raise BitrixError("Не задан BITRIX24_WEBHOOK_URL")
    try:
        response = requests.post(
            f"{settings.BITRIX24_WEBHOOK_URL}/{method}.json",
            json=params or {}, timeout=settings.BITRIX24_TIMEOUT,
        )
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        # Текст исключения requests может содержать URL вебхука с секретом — в журнал его не пишем.
        raise BitrixError(f"{method}: сетевая ошибка ({type(exc).__name__})") from None
    if "error" in data:
        raise BitrixError(f"{method}: {data.get('error')} — {data.get('error_description', '')}")
    return data.get("result")


def add_working_minutes(start, minutes, s):
    """Крайний срок с учётом рабочих часов и дней из настроек сайта."""
    cur = timezone.localtime(start)
    if s.work_end <= s.work_start:
        return cur + timedelta(minutes=minutes)
    remaining = float(minutes)
    for _ in range(370):
        day_start = cur.replace(hour=s.work_start.hour, minute=s.work_start.minute, second=0, microsecond=0)
        day_end = cur.replace(hour=s.work_end.hour, minute=s.work_end.minute, second=0, microsecond=0)
        if cur.isoweekday() in s.work_day_numbers and cur < day_end:
            cur = max(cur, day_start)
            available = (day_end - cur).total_seconds() / 60
            if remaining <= available:
                return cur + timedelta(minutes=remaining)
            remaining -= available
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return cur


def responsible_id(dealer, s):
    return dealer.country.bitrix_responsible_id or s.bitrix_default_responsible_id


def _lead_fields(dealer, s):
    comments = [
        f"Регистрация на сайте: {timezone.localtime(dealer.created_at):%d.%m.%Y %H:%M}",
        f"Страна: {dealer.country.name_ru}, город: {dealer.city}",
        f"Язык общения: {dealer.language}",
        f"Вид деятельности: {dealer.get_activity_display() or '—'}",
        f"Предполагаемый объём: {dealer.get_volume_display() or '—'}",
        f"Источник: {dealer.source_label}",
    ]
    if dealer.landing_page:
        comments.append(f"Страница входа: {dealer.landing_page}")
    if dealer.click_id:
        comments.append(f"Click ID: {dealer.click_id}")
    if dealer.comment:
        comments.append(f"Комментарий клиента: {dealer.comment}")
    fields = {
        "TITLE": f"{s.brand_name} · {dealer.company} · {dealer.country.name_ru}",
        "NAME": dealer.contact_name,
        "COMPANY_TITLE": dealer.company,
        "PHONE": [{"VALUE": dealer.phone, "VALUE_TYPE": "WORK"}],
        "ADDRESS_CITY": dealer.city,
        "ADDRESS_COUNTRY": dealer.country.name_ru,
        "SOURCE_ID": "WEB",
        "SOURCE_DESCRIPTION": f"Сайт {s.brand_name}: {dealer.source_label}",
        "COMMENTS": "<br>".join(comments),
        "ASSIGNED_BY_ID": responsible_id(dealer, s),
        "OPENED": "Y",
        "UTM_SOURCE": dealer.utm_source, "UTM_MEDIUM": dealer.utm_medium,
        "UTM_CAMPAIGN": dealer.utm_campaign, "UTM_TERM": dealer.utm_term,
        "UTM_CONTENT": dealer.utm_content,
    }
    if dealer.email:
        fields["EMAIL"] = [{"VALUE": dealer.email, "VALUE_TYPE": "WORK"}]
    return fields


def ensure_lead(dealer, s):
    """Создаёт лид или привязывает к существующему с тем же телефоном (без дублей)."""
    if dealer.bitrix_lead_id:
        return dealer.bitrix_lead_id
    found = call("crm.duplicate.findbycomm",
                 {"entity_type": "LEAD", "type": "PHONE", "values": [dealer.phone, "+" + dealer.phone_digits]})
    existing = found.get("LEAD") if isinstance(found, dict) else None
    if existing:
        lead_id = max(int(i) for i in existing)
        call("crm.timeline.comment.add", {"fields": {
            "ENTITY_ID": lead_id, "ENTITY_TYPE": "lead",
            "COMMENT": "Клиент повторно заполнил анкету на сайте.\n" + _lead_fields(dealer, s)["COMMENTS"].replace("<br>", "\n"),
        }})
    else:
        lead_id = int(call("crm.lead.add", {"fields": _lead_fields(dealer, s),
                                            "params": {"REGISTER_SONET_EVENT": "Y"}}))
    dealer.bitrix_lead_id = lead_id
    dealer.save(update_fields=["bitrix_lead_id"])
    return lead_id


def add_task(title, description, dealer, s, lead_id):
    deadline = add_working_minutes(timezone.now(), s.reaction_minutes, s)
    fields = {
        "TITLE": title, "DESCRIPTION": description,
        "RESPONSIBLE_ID": responsible_id(dealer, s),
        "DEADLINE": deadline.isoformat(timespec="seconds"),
        "UF_CRM_TASK": [f"L_{lead_id}"],
        "PRIORITY": 2,
    }
    if s.bitrix_head_id:
        fields["AUDITORS"] = [s.bitrix_head_id]
    result = call("tasks.task.add", {"fields": fields})
    return int(result["task"]["id"]), deadline


def ensure_contact_task(dealer, s):
    if dealer.bitrix_task_id:
        return dealer.bitrix_task_id
    task_id, deadline = add_task(
        f"Связаться с новым потенциальным дилером {s.brand_name}: {dealer.company} ({dealer.country.name_ru})",
        f"Контакт: {dealer.contact_name}, {dealer.phone} {dealer.email}\n"
        f"Город: {dealer.city}. Язык: {dealer.language}.\n"
        "После разговора зафиксируйте результат в карточке лида.",
        dealer, s, dealer.bitrix_lead_id,
    )
    dealer.bitrix_task_id, dealer.task_deadline, dealer.overdue_notified = task_id, deadline, False
    dealer.save(update_fields=["bitrix_task_id", "task_deadline", "overdue_notified"])
    return task_id


def order_text(order):
    rows = [f"Заказ с сайта № {order.number} от {timezone.localtime(order.created_at):%d.%m.%Y %H:%M}"]
    for item in order.items.all():
        rows.append(f"• {item.name} — {item.boxes} кор. × {item.price} = {item.amount} {order.currency}")
    rows.append(f"Итого: {order.total_amount} {order.currency}, коробок: {order.total_boxes}")
    if order.total_weight_kg is not None:
        rows.append(f"Вес брутто: {order.total_weight_kg} кг, объём: {order.total_volume_m3} м³")
    for key, c in (order.summary.get("containers") or {}).items():
        rows.append(f"Контейнер {key}': {c['count']} шт., загрузка {c['fill_percent']}% (предварительно)")
    if order.comment:
        rows.append(f"Комментарий клиента: {order.comment}")
    return "\n".join(rows)


def push_order(order, s, done):
    """Прикрепляет заказ к лиду (или сделке, если лид уже конвертирован). `done` — выполненные шаги."""
    dealer = order.dealer
    lead_id = ensure_lead(dealer, s)
    text = order_text(order)

    if "comment" not in done:
        entity_type, entity_id = "lead", lead_id
        lead = call("crm.lead.get", {"id": lead_id}) or {}
        if lead.get("STATUS_ID") == "CONVERTED":
            deals = call("crm.deal.list", {"filter": {"LEAD_ID": lead_id}, "select": ["ID"],
                                           "order": {"ID": "DESC"}})
            if deals:
                entity_type, entity_id = "deal", int(deals[0]["ID"])
        call("crm.timeline.comment.add", {"fields": {
            "ENTITY_ID": entity_id, "ENTITY_TYPE": entity_type, "COMMENT": text}})
        done["comment"] = f"{entity_type}:{entity_id}"

    if "amount" not in done:
        try:  # сумма не критична: валюта может быть не заведена в справочнике Bitrix24
            call("crm.lead.update", {"id": lead_id, "fields": {
                "OPPORTUNITY": str(order.total_amount), "CURRENCY_ID": order.currency}})
            done["amount"] = True
        except BitrixError as exc:
            done["amount"] = f"пропущено: {exc}"

    if "notify" not in done:
        call("im.notify.system.add", {
            "USER_ID": responsible_id(dealer, s),
            "MESSAGE": f"Новый заказ с сайта {s.brand_name}: {dealer.company}, "
                       f"{order.total_amount} {order.currency} (№ {order.number}). Лид #{lead_id}.",
        })
        done["notify"] = True

    if "task" not in done:
        task_id, _ = add_task(
            f"Обработать заказ {order.number}: {dealer.company} ({dealer.country.name_ru})",
            text, dealer, s, lead_id)
        done["task"] = task_id


def check_overdue(s):
    """Уведомляет руководителя продаж о просроченных задачах первого контакта."""
    from dealers.models import Dealer

    if not (is_configured() and s.bitrix_head_id):
        return 0
    notified = 0
    qs = Dealer.objects.filter(bitrix_task_id__isnull=False, overdue_notified=False,
                               task_deadline__lt=timezone.now()).select_related("country")
    for dealer in qs[:50]:
        try:
            task = (call("tasks.task.get", {"taskId": dealer.bitrix_task_id,
                                            "select": ["ID", "STATUS"]}) or {}).get("task") or {}
            if str(task.get("status")) not in ("4", "5"):  # 4 — ждёт контроля, 5 — завершена
                call("im.notify.system.add", {
                    "USER_ID": s.bitrix_head_id,
                    "MESSAGE": f"Просрочена задача #{dealer.bitrix_task_id}: связаться с дилером "
                               f"{dealer.company} ({dealer.country.name_ru}). Лид #{dealer.bitrix_lead_id}.",
                })
                notified += 1
            dealer.overdue_notified = True
            dealer.save(update_fields=["overdue_notified"])
        except BitrixError as exc:
            log.warning("Проверка просрочки не удалась: %s", exc)
    return notified
