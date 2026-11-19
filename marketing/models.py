from django.db import models


class MarketingMaterial(models.Model):
    KINDS = [
        ("video", "Рекламные видеоролики"),
        ("photo", "Фотографии продукции"),
        ("social", "Баннеры для Instagram и Facebook"),
        ("poster", "Плакаты для магазинов"),
        ("pos", "Материалы для торговых точек"),
        ("promo", "Маркетинговые акции"),
        ("terms", "Условия маркетинговой поддержки"),
    ]

    kind = models.CharField("Раздел", max_length=10, choices=KINDS)
    title = models.CharField("Название", max_length=160)
    description = models.TextField("Описание", blank=True)
    preview = models.ImageField("Превью", upload_to="marketing/preview/", blank=True)
    file = models.FileField("Файл для скачивания", upload_to="protected/marketing/", blank=True,
                            help_text="Хранится в закрытой папке, отдаётся только через сайт.")
    video_url = models.URLField("Ссылка на видео (YouTube и т.п.)", blank=True)
    dealers_only = models.BooleanField("Скачивание только для зарегистрированных дилеров", default=True)
    is_active = models.BooleanField("Показывать", default=True)
    sort = models.PositiveIntegerField("Порядок", default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Маркетинговый материал"
        verbose_name_plural = "Маркетинговые материалы"
        ordering = ["kind", "sort", "-created_at"]

    def __str__(self):
        return self.title
