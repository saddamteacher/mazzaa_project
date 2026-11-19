"""Первичное наполнение сайта: роли, страны и валюты, линейка MAZZAA, баннеры.
Команда безопасна для повторного запуска — существующие записи не перезаписываются.
С флагом --demo добавляет ДЕМО-габариты коробок и ДЕМО-цены (для проверки калькулятора)."""
from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from catalog.models import Country, Currency, Flavor, Price, Product, WeightCategory
from core.models import Banner, SiteSettings

COUNTRIES = [  # код, RU, EN, валюта, название валюты, примерный курс к USD (только для демо-цен)
    ("kz", "Казахстан", "Kazakhstan", "KZT", "Казахстанский тенге", 520),
    ("kg", "Кыргызстан", "Kyrgyzstan", "KGS", "Киргизский сом", 87),
    ("tj", "Таджикистан", "Tajikistan", "TJS", "Таджикский сомони", 10.6),
    ("ru", "Россия", "Russia", "RUB", "Российский рубль", 90),
    ("by", "Беларусь", "Belarus", "BYN", "Белорусский рубль", 3.3),
    ("az", "Азербайджан", "Azerbaijan", "AZN", "Азербайджанский манат", 1.7),
    ("am", "Армения", "Armenia", "AMD", "Армянский драм", 390),
    ("ge", "Грузия", "Georgia", "GEL", "Грузинский лари", 2.7),
    ("tm", "Туркменистан", "Turkmenistan", "TMT", "Туркменский манат", 3.5),
    ("md", "Молдова", "Moldova", "MDL", "Молдавский лей", 17.5),
]
WEIGHTS = [  # граммы, упаковка RU, EN, шт. в коробке
    (40, "Пакет", "Pillow pack", 48),
    (50, "Упаковка в форме пламени", "Flame-shaped pack", 18),
    (100, "Дой-пак (Doypack)", "Doypack (stand-up pouch)", 12),
    (150, "Большая упаковка", "Sharing pack", None),  # количество в коробке ещё не определено
]
FLAVORS = [  # slug, RU, EN, цвет, острота
    ("sticks", "Остро-сладкие палочки", "Sweet & spicy sticks", "#f2b705", 3),
    ("squares", "Остро-сладкие квадратики", "Sweet & spicy squares", "#7b1fa2", 3),
    ("chili", "Острый чили", "Hot chili", "#e5171e", 5),
    ("cheese", "Остро-сладкий сыр", "Sweet & spicy cheese", "#f28c0f", 3),
    ("mustard", "Остро-сладкая горчица (васаби)", "Sweet & spicy mustard (wasabi)", "#b7a40e", 4),
    ("lamb", "Остро-сладкая баранина", "Sweet & spicy lamb", "#a3260f", 4),
]
PRODUCTS = [  # slug, вкус, вес, RU, EN
    ("sticks-40", "sticks", 40, "MAZZAA Crispy «Остряш» — чипсы-палочки", "MAZZAA Crispy “Ostryash” — chip sticks"),
    ("squares-40", "squares", 40, "MAZZAA Crispy «Жгучеслад» — чипсы-квадратики", "MAZZAA Crispy “Zhgucheslad” — square chips"),
] + [
    (f"{f}-{w}", f, w, f"MAZZAA острые чипсы со вкусом {ru}", f"MAZZAA spicy chips — {en}")
    for w in (50, 100, 150)
    for f, ru, en in [("chili", "острого чили", "hot chili"), ("cheese", "остро-сладкого сыра", "sweet & spicy cheese"),
                      ("mustard", "остро-сладкой горчицы (васаби)", "sweet & spicy mustard (wasabi)"),
                      ("lamb", "остро-сладкой баранины", "sweet & spicy lamb")]
]
DESCRIPTION = (
    "Острые чипсы MAZZAA для тех, кто любит яркие вкусы. Состав: мука пшеничная, мука кукурузная, "
    "кукурузный и картофельный крахмал, растительное масло, соль йодированная, вкусо-ароматическая добавка. "
    "Срок годности — 6 месяцев. Произведено в Узбекистане.",
    "MAZZAA spicy chips for those who love bold flavours. Ingredients: wheat flour, corn flour, corn and potato "
    "starch, vegetable oil, iodized salt, flavouring. Shelf life: 6 months. Made in Uzbekistan.",
)
DEMO = {  # вес: (Д, Ш, В см; брутто кг; коробок на паллете; цена коробки в USD) — ДЕМО, заменить реальными
    40: (40, 30, 30, "2.4", 60, "9.60"),
    50: (38, 28, 26, "1.3", 80, "5.40"),
    100: (40, 30, 28, "1.6", 64, "6.60"),
    150: (45, 32, 30, "2.2", 48, "9.00"),
}
ROLES = {
    "Контент-менеджер": ["product", "productimage", "flavor", "weightcategory", "banner", "uitext", "marketingmaterial"],
    "Менеджер цен": ["price", "pricehistory", "currency", "country"],
    "Менеджер продаж": ["dealer", "order", "orderitem", "crmjob"],
}


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="добавить демо-габариты и демо-цены")

    def handle(self, *args, demo=False, **options):
        for role, models in ROLES.items():
            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.add(*Permission.objects.filter(content_type__model__in=models))

        s = SiteSettings.load()
        if not s.about_text:
            s.about_title_ru, s.about_title_en = "QOSIMOV GROUP — производитель MAZZAA", "QOSIMOV GROUP — the maker of MAZZAA"
            s.about_text_ru = ("QOSIMOV GROUP — производитель снеков из Узбекистана. Бренд MAZZAA — это узнаваемая линейка острых "
                               "и остро-сладких чипсов для молодёжи и взрослых, которые любят острые ощущения и насыщенные вкусы.\n\n"
                               "Мы развиваем экспорт в страны СНГ и Кавказа и ищем дистрибьюторов, готовых расти вместе с брендом.")
            s.about_text_en = ("QOSIMOV GROUP is a snack manufacturer from Uzbekistan. MAZZAA is a recognisable range of hot and "
                               "sweet-and-spicy chips for young people and adults who love bold sensations and rich flavours.\n\n"
                               "We are expanding exports across the CIS and the Caucasus and are looking for distributors ready to grow with the brand.")
            s.address_ru = "Узбекистан, г. Ташкент, Учтепинский район, ул. Фархад, 20"
            s.address_en = "20 Farhod Street, Uchtepa district, Tashkent, Uzbekistan"
            s.phone, s.whatsapp = "+998 90 391 00 40", "998903910040"
            s.instagram = "https://www.instagram.com/mazzaa_uz"
            s.save()

        for i, (code, ru, en, cur, cur_name, _rate) in enumerate(COUNTRIES):
            currency, _ = Currency.objects.get_or_create(code=cur, defaults={"name": cur_name})
            Country.objects.get_or_create(code=code, defaults={
                "name_ru": ru, "name_en": en, "currency": currency, "sort": (i + 1) * 10,
                "landing_enabled": code in ("kz", "az", "ru")})
        for i, (grams, ru, en, _n) in enumerate(WEIGHTS):
            WeightCategory.objects.get_or_create(grams=grams, defaults={
                "package_note_ru": ru, "package_note_en": en, "sort": (i + 1) * 10})
        for i, (slug, ru, en, color, heat) in enumerate(FLAVORS):
            Flavor.objects.get_or_create(slug=slug, defaults={
                "name_ru": ru, "name_en": en, "color": color, "heat": heat, "sort": (i + 1) * 10})

        per_box = {grams: n for grams, _ru, _en, n in WEIGHTS}
        for i, (slug, flavor, grams, ru, en) in enumerate(PRODUCTS):
            Product.objects.get_or_create(slug=slug, defaults={
                "name_ru": ru, "name_en": en, "description_ru": DESCRIPTION[0], "description_en": DESCRIPTION[1],
                "flavor": Flavor.objects.get(slug=flavor), "weight": WeightCategory.objects.get(grams=grams),
                "packs_per_box": per_box[grams], "sort": (i + 1) * 10})

        if not Banner.objects.exists():
            for i, (ru, en, sub_ru, sub_en, link, theme) in enumerate([
                ("Наша продукция", "Our products", "14 позиций: 40, 50, 100 и 150 г", "14 products: 40, 50, 100 and 150 g", "/catalog/", "fire"),
                ("Калькулятор заказа", "Order calculator", "Стоимость, вес, объём и контейнеры", "Cost, weight, volume and containers", "/calculator/", "gold"),
                ("Маркетинговая поддержка", "Marketing support", "Видео, баннеры и материалы для магазинов", "Videos, banners and in-store materials", "/marketing/", "dark"),
            ]):
                Banner.objects.create(title_ru=ru, title_en=en, subtitle_ru=sub_ru, subtitle_en=sub_en,
                                      link=link, theme=theme, sort=(i + 1) * 10)

        if demo:
            rates = {code: rate for code, *_rest, rate in COUNTRIES}
            for p in Product.objects.select_related("weight"):
                l, w, h, gross, pallet, usd = DEMO[p.weight.grams]
                if not p.has_dimensions:
                    p.box_length_cm, p.box_width_cm, p.box_height_cm = l, w, h
                    p.gross_weight_kg, p.boxes_per_pallet = Decimal(gross), pallet
                    p.save()
                for country in Country.objects.all():
                    price = (Decimal(usd) * Decimal(str(rates.get(country.code, 1)))).quantize(Decimal("1"))
                    Price.objects.get_or_create(product=p, country=country, defaults={"price": price})
            self.stdout.write(self.style.WARNING("Добавлены ДЕМО-габариты и ДЕМО-цены — замените реальными в админ-панели."))
        self.stdout.write(self.style.SUCCESS(f"Готово: товаров {Product.objects.count()}, стран {Country.objects.count()}."))
