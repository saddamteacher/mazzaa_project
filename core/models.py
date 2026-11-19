from datetime import time

from django.db import models


class SiteSettings(models.Model):
    """Единственная запись с настройками сайта (редактируется в админ-панели)."""

    ACCESS_AUTO = "auto"
    ACCESS_MANUAL = "manual"

    brand_name = models.CharField("Название бренда", max_length=40, default="MAZZAA")
    logo = models.FileField("Логотип (SVG/PNG)", upload_to="brand/", blank=True)
    hero_video = models.FileField("Видео в шапке главной (MP4)", upload_to="brand/", blank=True,
                                  help_text="Короткий ролик без звука, до ~5 МБ. Пусто — используется ролик по умолчанию.")
    company_name = models.CharField("Компания", max_length=120, default="QOSIMOV GROUP")
    about_title = models.CharField("О компании: заголовок", max_length=160, blank=True)
    about_text = models.TextField("О компании: текст", blank=True)
    address = models.CharField("Адрес", max_length=250, blank=True)
    phone = models.CharField("Телефон", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    whatsapp = models.CharField("WhatsApp (номер, только цифры)", max_length=20, blank=True)
    telegram = models.CharField("Telegram (имя без @)", max_length=60, blank=True)
    instagram = models.URLField("Instagram", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    privacy_text = models.TextField("Политика конфиденциальности", blank=True)

    price_access_mode = models.CharField(
        "Доступ к ценам", max_length=10, default=ACCESS_AUTO,
        choices=[(ACCESS_AUTO, "Автоматически после анкеты"), (ACCESS_MANUAL, "После одобрения менеджером")],
    )
    price_terms = models.CharField(
        "Условия поставки в прайсе", max_length=120, blank=True,
        help_text="Например: EXW Ташкент. Выводится в прайсе и коммерческом предложении.",
    )

    # Аналитика и реклама
    gtm_id = models.CharField("Google Tag Manager ID (GTM-XXXX)", max_length=20, blank=True)
    ga4_id = models.CharField("Google Analytics 4 ID (G-XXXX)", max_length=20, blank=True,
                              help_text="Не нужен, если GA4 подключён внутри GTM.")
    google_ads_id = models.CharField("Google Ads ID (AW-XXXX)", max_length=24, blank=True)
    google_ads_lead_label = models.CharField("Google Ads: метка конверсии «Регистрация»", max_length=60, blank=True)
    google_ads_order_label = models.CharField("Google Ads: метка конверсии «Заказ»", max_length=60, blank=True)
    meta_pixel_id = models.CharField("Meta Pixel ID", max_length=24, blank=True)
    gsc_verification = models.CharField("Google Search Console: код подтверждения", max_length=120, blank=True)

    # Bitrix24: регламент обработки
    bitrix_default_responsible_id = models.PositiveIntegerField(
        "Bitrix24: ID менеджера по умолчанию", default=1)
    bitrix_head_id = models.PositiveIntegerField(
        "Bitrix24: ID руководителя продаж", null=True, blank=True,
        help_text="Наблюдатель в задачах, получает уведомления о просрочке.")
    reaction_minutes = models.PositiveIntegerField("Срок реакции менеджера, рабочих минут", default=60)
    work_start = models.TimeField("Начало рабочего дня", default=time(9, 0))
    work_end = models.TimeField("Конец рабочего дня", default=time(18, 0))
    work_days = models.CharField("Рабочие дни (1=Пн … 7=Вс)", max_length=20, default="1,2,3,4,5")

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def work_day_numbers(self):
        return {int(d) for d in self.work_days.replace(" ", "").split(",") if d.isdigit()} or {1, 2, 3, 4, 5}


class Banner(models.Model):
    """Большой кликабельный баннер на главной странице."""

    THEMES = [("fire", "Огонь (красный)"), ("gold", "Золото (жёлтый)"), ("dark", "Уголь (тёмный)")]

    title = models.CharField("Заголовок", max_length=80)
    subtitle = models.CharField("Подзаголовок", max_length=200, blank=True)
    image = models.ImageField("Картинка", upload_to="banners/", blank=True)
    link = models.CharField("Ссылка", max_length=200, help_text="Напр. /catalog/ или полный URL")
    theme = models.CharField("Оформление", max_length=10, choices=THEMES, default="fire")
    is_active = models.BooleanField("Показывать", default=True)
    sort = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Баннер главной"
        verbose_name_plural = "Баннеры главной"
        ordering = ["sort", "id"]

    def __str__(self):
        return self.title


class UiText(models.Model):
    """Переопределение текста интерфейса. Пустое поле = текст по умолчанию из кода."""

    key = models.CharField("Ключ", max_length=80, unique=True)
    text = models.TextField("Текст", blank=True)

    class Meta:
        verbose_name = "Текст интерфейса"
        verbose_name_plural = "Тексты интерфейса (переводы)"
        ordering = ["key"]

    def __str__(self):
        return self.key
