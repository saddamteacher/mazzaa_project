from django.db import models


class Order(models.Model):
    number = models.CharField("Номер", max_length=20, unique=True, blank=True)
    dealer = models.ForeignKey("dealers.Dealer", on_delete=models.PROTECT, related_name="orders", verbose_name="Дилер")
    country = models.ForeignKey("catalog.Country", on_delete=models.PROTECT, verbose_name="Страна прайса")
    currency = models.CharField("Валюта", max_length=3)
    total_amount = models.DecimalField("Сумма", max_digits=16, decimal_places=2)
    total_boxes = models.PositiveIntegerField("Коробок")
    total_weight_kg = models.DecimalField("Вес брутто, кг", max_digits=12, decimal_places=2, null=True)
    total_volume_m3 = models.DecimalField("Объём, м³", max_digits=12, decimal_places=3, null=True)
    summary = models.JSONField("Расчёт логистики", default=dict, blank=True)
    comment = models.TextField("Комментарий клиента", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.number or f"#{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.number:
            self.number = f"MZ-{self.created_at:%y%m}-{self.pk:05d}"
            super().save(update_fields=["number"])


class OrderItem(models.Model):
    """Строка заказа. Цена и название фиксируются на момент отправки."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, verbose_name="Товар")
    name = models.CharField("Название на момент заказа", max_length=250)
    boxes = models.PositiveIntegerField("Коробок")
    price = models.DecimalField("Цена за коробку", max_digits=14, decimal_places=2)
    amount = models.DecimalField("Сумма", max_digits=16, decimal_places=2)

    class Meta:
        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"
