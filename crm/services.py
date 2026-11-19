"""Надёжная передача в Bitrix24: каждая заявка сначала сохраняется в очереди (CrmJob),
затем отправляется. При сбое — повтор с нарастающей паузой (команда process_crm_queue)."""
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from core.models import SiteSettings

from . import bitrix
from .models import CrmJob

log = logging.getLogger(__name__)


def enqueue(kind, dealer, order=None):
    job = CrmJob.objects.create(kind=kind, dealer=dealer, order=order)
    run_job(job)
    return job


def run_job(job):
    if job.status == CrmJob.DONE:
        return job
    if not bitrix.is_configured():
        job.last_error = "Bitrix24 не подключён: задайте BITRIX24_WEBHOOK_URL. Заявка сохранена и будет передана позже."
        job.next_attempt_at = timezone.now() + timedelta(minutes=10)
        job.save()
        return job
    s = SiteSettings.load()
    try:
        if job.kind == CrmJob.LEAD:
            job.result["lead_id"] = bitrix.ensure_lead(job.dealer, s)
            job.result["task_id"] = bitrix.ensure_contact_task(job.dealer, s)
        else:
            bitrix.push_order(job.order, s, job.result)
        job.status, job.done_at, job.last_error = CrmJob.DONE, timezone.now(), ""
    except Exception as exc:  # любая ошибка не должна ломать сайт для клиента
        job.attempts += 1
        job.last_error = str(exc)[:2000]
        job.status = CrmJob.FAILED if job.attempts >= settings.CRM_MAX_ATTEMPTS else CrmJob.PENDING
        job.next_attempt_at = timezone.now() + timedelta(minutes=min(2 ** job.attempts, 720))
        log.warning("Bitrix24: передача #%s не удалась (попытка %s): %s", job.pk, job.attempts, exc)
    job.save()
    return job


def process_queue(limit=50):
    jobs = CrmJob.objects.filter(status=CrmJob.PENDING, next_attempt_at__lte=timezone.now()) \
        .select_related("dealer__country", "order").order_by("created_at")[:limit]
    return sum(1 for job in jobs if run_job(job).status == CrmJob.DONE)
