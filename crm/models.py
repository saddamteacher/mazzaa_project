from django.db import models
from django.utils import timezone


class CrmJob(models.Model):
    """Очередь передачи в Bitrix24: журнал, ошибки и повторные попытки."""

    LEAD, ORDER = "lead", "order"
    KINDS = [(LEAD, "Создание лида и задачи"), (ORDER, "Передача заказа")]
    PENDING, DONE, FAILED = "pending", "done", "failed"
    STATUSES = [(PENDING, "В очереди"), (DONE, "Передано"), (FAILED, "Ошибка (попытки исчерпаны)")]

    kind = models.CharField("Тип", max_length=10, choices=KINDS)
    dealer = models.ForeignKey("dealers.Dealer", on_delete=models.CASCADE, related_name="crm_jobs", verbose_name="Дилер")
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.CASCADE,
                              related_name="crm_jobs", verbose_name="Заказ")
    status = models.CharField("Статус", max_length=10, choices=STATUSES, default=PENDING)
    attempts = models.PositiveIntegerField("Попыток", default=0)
    last_error = models.TextField("Последняя ошибка", blank=True)
    result = models.JSONField("Результат", default=dict, blank=True)
    next_attempt_at = models.DateTimeField("Следующая попытка", default=timezone.now)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    done_at = models.DateTimeField("Передано", null=True, blank=True)

    class Meta:
        verbose_name = "Передача в Bitrix24"
        verbose_name_plural = "Журнал передачи в Bitrix24"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.dealer}"
