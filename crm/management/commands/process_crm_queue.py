from django.core.management.base import BaseCommand

from core.models import SiteSettings
from crm import bitrix, services


class Command(BaseCommand):
    help = "Повторная передача заявок в Bitrix24 и контроль просроченных задач. Запускать по cron каждые 5–10 минут."

    def handle(self, *args, **options):
        sent = services.process_queue()
        overdue = bitrix.check_overdue(SiteSettings.load())
        self.stdout.write(f"Передано: {sent}; уведомлений о просрочке: {overdue}")
