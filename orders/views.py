import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalog.models import Product, WeightCategory, price_map
from core import i18n
from core.documents import file_response
from core.models import SiteSettings
from crm import services
from crm.models import CrmJob
from dealers.access import current_dealer, push_event

from . import calc
from .models import Order, OrderItem


def _access(request):
    dealer = current_dealer(request)
    return dealer if dealer and dealer.has_access else None


def calculator(request):
    dealer = _access(request)
    prices = price_map(dealer.country) if dealer else {}
    products = Product.objects.filter(is_active=True).select_related("flavor", "weight")
    if dealer:
        products = [p for p in products if p.pk in prices]  # скрытые из прайса страны не показываем
    weights = list(WeightCategory.objects.all())
    for w in weights:
        w.items = [p for p in products if p.weight_id == w.pk]
        for p in w.items:
            p.price = prices.get(p.pk)
    return render(request, "calculator.html", {
        "weights": [w for w in weights if w.items],
        "currency": dealer.country.currency.code if dealer else "",
        "labels": {k: i18n.t(f"calc.{k}") for k in ("remove", "partial", "fill")}
        | {"kg": i18n.t("unit.kg"), "m3": i18n.t("unit.m3"), "boxes": i18n.t("unit.boxes_short")},
    })


def _items_from(request):
    try:
        raw = json.loads(request.POST.get("items") or request.body or "[]")
    except (ValueError, UnicodeDecodeError):
        raw = []
    if isinstance(raw, dict):
        raw = raw.get("items", [])
    return calc.parse_items(raw)


@require_POST
def api_calc(request):
    dealer = _access(request)
    result = calc.calculate(_items_from(request), dealer.country if dealer else None)
    return JsonResponse(calc.to_json(result))


def _offer_doc(result, dealer, s, title):
    t = i18n.t
    cur = result["currency"]
    rows = [[n, f"{l['name']} · {l['weight_g']} {t('unit.g')}", l["boxes"], l["packs"], l["price"], l["amount"],
             l["weight_kg"], l["volume_m3"]] for n, l in enumerate(result["lines"], start=1)]
    notes = []
    if result["pallets"]:
        notes.append(f"{t('calc.pallets')}: {result['pallets']}")
    for key, c in result["containers"].items():
        notes.append(f"{t('calc.container')} {key}′ × {c['count']} — {t('calc.fill')} {c['fill_percent']}%")
    notes += [t("calc.disclaimer"), t("doc.offer_note"), f"{s.company_name} · {s.phone} · {s.email}"]
    return {
        "title": title,
        "meta": [f"{t('doc.date')}: {timezone.localdate():%d.%m.%Y}",
                 f"{t('doc.for')}: {dealer.company}, {dealer.city}, {dealer.country.name}",
                 f"{t('doc.terms')}: {s.price_terms or t('doc.terms_tbd')}"],
        "headers": ["№", t("col.product"), t("col.boxes"), t("col.packs"), f"{t('col.price_box')}, {cur}",
                    f"{t('col.amount')}, {cur}", t("col.gross_kg"), t("col.volume_m3")],
        "rows": rows,
        "totals": [["", t("calc.total"), result["total_boxes"], "", "", result["total_amount"],
                    result["total_weight_kg"], result["total_volume_m3"]]],
        "notes": notes,
    }


@require_POST
def offer(request, fmt):
    """Коммерческое предложение по текущему расчёту (без оформления заказа)."""
    dealer = _access(request)
    if not dealer:
        return redirect(f"{reverse('register')}?next={reverse('calculator')}")
    result = calc.calculate(_items_from(request), dealer.country)
    if not result["lines"]:
        return redirect("calculator")
    s = SiteSettings.load()
    doc = _offer_doc(result, dealer, s, f"{s.brand_name} — {i18n.t('doc.offer')}")
    return file_response(doc, fmt, f"mazzaa-offer-{timezone.localdate():%Y%m%d}")


@require_POST
def submit(request):
    dealer = _access(request)
    if not dealer:
        return redirect(f"{reverse('register')}?next={reverse('calculator')}")
    result = calc.calculate(_items_from(request), dealer.country)  # цены берём только с сервера
    if not result["lines"]:
        return redirect("calculator")
    with transaction.atomic():
        order = Order.objects.create(
            dealer=dealer, country=dealer.country, currency=result["currency"],
            total_amount=result["total_amount"], total_boxes=result["total_boxes"],
            total_weight_kg=result["total_weight_kg"], total_volume_m3=result["total_volume_m3"],
            summary=calc.to_json({k: result[k] for k in ("pallets", "containers", "weight_complete", "volume_complete")}),
            comment=request.POST.get("comment", "")[:2000],
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product_id=l["id"], name=f"{l['name']} · {l['weight_g']} г",
                      boxes=l["boxes"], price=l["price"], amount=l["amount"])
            for l in result["lines"]
        ])
    services.enqueue(CrmJob.ORDER, dealer, order)
    push_event(request, "order_submit", value=float(order.total_amount), currency=order.currency,
               order_id=order.number)
    return redirect("order_done", number=order.number)


def order_done(request, number):
    dealer = current_dealer(request)
    order = get_object_or_404(Order, number=number, dealer=dealer)
    return render(request, "order_done.html", {"order": order})


def order_offer(request, number, fmt):
    dealer = current_dealer(request)
    order = get_object_or_404(Order, number=number, dealer=dealer)
    s = SiteSettings.load()
    t = i18n.t
    items = {i.product_id: i for i in order.items.select_related("product__weight")}
    # Документ по заказу строится из сохранённых цен, а не из текущего прайса.
    lines = [{"name": i.name.rsplit(" · ", 1)[0], "weight_g": i.product.weight.grams, "boxes": i.boxes,
              "packs": i.product.packs_per_box * i.boxes if i.product.packs_per_box else None,
              "price": i.price, "amount": i.amount,
              "weight_kg": i.product.gross_weight_kg * i.boxes if i.product.gross_weight_kg else None,
              "volume_m3": i.product.volume_m3 * i.boxes if i.product.volume_m3 else None}
             for i in items.values()]
    result = {"lines": lines, "currency": order.currency, "total_boxes": order.total_boxes,
              "total_amount": order.total_amount, "total_weight_kg": order.total_weight_kg,
              "total_volume_m3": order.total_volume_m3, "pallets": order.summary.get("pallets"),
              "containers": order.summary.get("containers") or {}}
    doc = _offer_doc(result, dealer, s, f"{s.brand_name} — {t('doc.order')} {order.number}")
    return file_response(doc, fmt, f"mazzaa-{order.number}")
