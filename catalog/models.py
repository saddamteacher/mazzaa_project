from decimal import Decimal

from django.conf import settings
from django.db import models


class Currency(models.Model):
    code = models.CharField("Код (ISO 4217)", max_length=3, unique=True)
    name = models.CharField("Название", max_length=60)
    symbol = models.CharField("Символ", max_length=8, blank=True)

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ["code"]

    def __str__(self):
        return self.code


class Country(models.Model):
    code = models.SlugField("Код страны (ISO, напр. kz)", max_length=2, unique=True)
    name = models.CharField("Название", max_length=80)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="Валюта прайса")
    is_active = models.BooleanField("Доступна в анкете", default=True)
    sort = models.PositiveIntegerField("Порядок", default=100)
    bitrix_responsible_id = models.PositiveIntegerField(
        "ID ответственного менеджера в Bitrix24", null=True, blank=True,
        help_text="Лиды из этой страны назначаются этому сотруднику. Пусто — менеджер по умолчанию.",
    )
    landing_enabled = models.BooleanField("Посадочная страница включена", default=False)
    landing_title = models.CharField("Заголовок посадочной", max_length=160, blank=True)
    landing_text = models.TextField("Текст посадочной", blank=True)

    class Meta:
        verbose_name = "Страна / рынок"
        verbose_name_plural = "Страны и рынки"
        ordering = ["sort", "name"]

    def __str__(self):
        return self.name


class WeightCategory(models.Model):
    grams = models.PositiveIntegerField("Вес упаковки, г", unique=True)
    package_note = models.CharField("Тип упаковки", max_length=120, blank=True)
    sort = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Весовая категория"
        verbose_name_plural = "Весовые категории"
        ordering = ["sort", "grams"]

    def __str__(self):
        return f"{self.grams} г"


class Flavor(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField("Вкус", max_length=120)
    color = models.CharField("Цвет (hex)", max_length=7, default="#e5171e")
    heat = models.PositiveSmallIntegerField("Острота (1–5)", default=3)
    sort = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Вкус"
        verbose_name_plural = "Вкусы"
        ordering = ["sort", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    slug = models.SlugField(unique=True)
    sku = models.CharField("Артикул", max_length=40, blank=True)
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    flavor = models.ForeignKey(Flavor, on_delete=models.PROTECT, verbose_name="Вкус")
    weight = models.ForeignKey(WeightCategory, on_delete=models.PROTECT, verbose_name="Весовая категория")
    image = models.ImageField("Главное фото", upload_to="products/", blank=True)
    packs_per_box = models.PositiveIntegerField("Упаковок в коробке", null=True, blank=True)
    box_length_cm = models.DecimalField("Длина коробки, см", max_digits=6, decimal_places=1, null=True, blank=True)
    box_width_cm = models.DecimalField("Ширина коробки, см", max_digits=6, decimal_places=1, null=True, blank=True)
    box_height_cm = models.DecimalField("Высота коробки, см", max_digits=6, decimal_places=1, null=True, blank=True)
    gross_weight_kg = models.DecimalField("Вес брутто коробки, кг", max_digits=7, decimal_places=3, null=True, blank=True)
    volume_m3 = models.DecimalField(
        "Объём коробки, м³", max_digits=8, decimal_places=5, null=True, blank=True,
        help_text="Оставьте пустым — рассчитается из габаритов.",
    )
    boxes_per_pallet = models.PositiveIntegerField("Коробок на паллете", null=True, blank=True)
    is_active = models.BooleanField("Показывать на сайте", default=True)
    sort = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["weight__sort", "weight__grams", "sort", "id"]

    def __str__(self):
        return f"{self.name} · {self.weight}"

    @property
    def has_dimensions(self):
        return bool(self.box_length_cm and self.box_width_cm and self.box_height_cm)

    def save(self, *args, **kwargs):
        if self.volume_m3 is None and self.has_dimensions:
            vol = self.box_length_cm * self.box_width_cm * self.box_height_cm / Decimal(1_000_000)
            self.volume_m3 = vol.quantize(Decimal("0.00001"))
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("Фото", upload_to="products/")
    sort = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ["sort", "id"]


class Price(models.Model):
    """Цена за одну коробку товара для конкретной страны. Задаётся только вручную."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices", verbose_name="Товар")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="prices", verbose_name="Страна")
    price = models.DecimalField("Цена за коробку", max_digits=14, decimal_places=2)
    is_hidden = models.BooleanField("Скрыть из прайса страны", default=False)
    updated_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены по странам"
        unique_together = [("product", "country")]
        ordering = ["country__sort", "product__weight__grams", "product__sort"]

    def __str__(self):
        return f"{self.product} — {self.country}: {self.price}"

    def save(self, *args, **kwargs):
        old = None
        if self.pk:
            old = Price.objects.filter(pk=self.pk).values("price", "is_hidden").first()
        super().save(*args, **kwargs)
        if old is None or old["price"] != self.price or old["is_hidden"] != self.is_hidden:
            PriceHistory.objects.create(
                product=self.product, country=self.country,
                old_price=old["price"] if old else None, new_price=self.price,
                is_hidden=self.is_hidden, changed_by=getattr(self, "_changed_by", None),
            )


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    old_price = models.DecimalField("Старая цена", max_digits=14, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField("Новая цена", max_digits=14, decimal_places=2)
    is_hidden = models.BooleanField("Скрыта", default=False)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Кто изменил"
    )
    changed_at = models.DateTimeField("Когда", auto_now_add=True)

    class Meta:
        verbose_name = "Запись истории цен"
        verbose_name_plural = "История изменения цен"
        ordering = ["-changed_at"]


def price_map(country):
    """{product_id: Decimal} — видимые цены активных товаров для страны."""
    return dict(
        Price.objects.filter(country=country, is_hidden=False, product__is_active=True)
        .values_list("product_id", "price")
    )
