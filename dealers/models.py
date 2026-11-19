import re
import uuid

from django.db import models

ACTIVITY_CHOICES = [
    ("distributor", "Дистрибьютор"),
    ("wholesale", "Оптовая торговля"),
    ("retail_chain", "Розничная сеть"),
    ("horeca", "HoReCa"),
    ("online", "Онлайн-торговля / маркетплейсы"),
    ("other", "Другое"),
]
VOLUME_CHOICES = [
    ("trial", "Пробная партия"),
    ("lt20", "Меньше 20-футового контейнера"),
    ("c20", "20-футовый контейнер"),
    ("c40", "40-футовый контейнер"),
    ("regular", "Регулярные поставки, несколько контейнеров"),
]


def normalize_phone(phone):
    return re.sub(r"\D", "", phone or "")


class Dealer(models.Model):
    PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
    STATUSES = [(PENDING, "Ожидает одобрения"), (APPROVED, "Доступ открыт"), (REJECTED, "Отклонён")]

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField("Доступ к ценам", max_length=10, choices=STATUSES, default=PENDING)
    country = models.ForeignKey("catalog.Country", on_delete=models.PROTECT, verbose_name="Страна")
    city = models.CharField("Город", max_length=120)
    company = models.CharField("Компания", max_length=200)
    contact_name = models.CharField("Контактное лицо", max_length=160)
    phone = models.CharField("Телефон / WhatsApp", max_length=40)
    phone_digits = models.CharField(max_length=20, db_index=True, editable=False)
    email = models.EmailField("E-mail", blank=True)
    activity = models.CharField("Вид деятельности", max_length=20, choices=ACTIVITY_CHOICES, blank=True)
    volume = models.CharField("Предполагаемый объём", max_length=20, choices=VOLUME_CHOICES, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    language = models.CharField("Язык", max_length=5, default="ru")

    utm_source = models.CharField(max_length=200, blank=True)
    utm_medium = models.CharField(max_length=200, blank=True)
    utm_campaign = models.CharField(max_length=200, blank=True)
    utm_term = models.CharField(max_length=200, blank=True)
    utm_content = models.CharField(max_length=200, blank=True)
    click_id = models.CharField("gclid / fbclid", max_length=300, blank=True)
    referrer = models.CharField("Источник перехода", max_length=500, blank=True)
    landing_page = models.CharField("Страница входа", max_length=500, blank=True)

    bitrix_lead_id = models.PositiveIntegerField("ID лида в Bitrix24", null=True, blank=True)
    bitrix_task_id = models.PositiveIntegerField("ID задачи в Bitrix24", null=True, blank=True)
    task_deadline = models.DateTimeField("Крайний срок задачи", null=True, blank=True)
    overdue_notified = models.BooleanField("Руководитель уведомлён о просрочке", default=False)

    ip = models.GenericIPAddressField(null=True, blank=True)
    consent_at = models.DateTimeField("Согласие на обработку данных", null=True, blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Дилер (анкета)"
        verbose_name_plural = "Дилеры (анкеты)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} ({self.country})"

    def save(self, *args, **kwargs):
        self.phone_digits = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    @property
    def has_access(self):
        return self.status == self.APPROVED

    @property
    def source_label(self):
        if self.utm_source:
            return f"{self.utm_source} / {self.utm_medium or '-'}"
        return self.referrer or "direct"
