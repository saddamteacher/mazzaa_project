"""Тексты интерфейса. Значения по умолчанию лежат здесь; администратор может
переопределить любой текст в админ-панели («Тексты интерфейса»), не трогая код.
Новый язык: добавьте его в settings.LANGUAGES — недостающие тексты берутся из английского."""
import time

from django.conf import settings
from django.utils.translation import get_language

S = STRINGS = {}


def _(key, ru, en):
    S[key] = {"ru": ru, "en": en}


# --- Общие -------------------------------------------------------------------
_("meta.title", "Острые чипсы оптом от производителя", "Spicy chips wholesale from the manufacturer")
_("meta.description", "MAZZAA — острые и остро-сладкие чипсы из Узбекистана. Оптовые поставки и дистрибуция в страны СНГ и Кавказа: региональные цены, калькулятор заказа, маркетинговая поддержка.",
  "MAZZAA — hot and sweet-and-spicy chips from Uzbekistan. Wholesale supply and distribution across the CIS and the Caucasus: regional prices, order calculator, marketing support.")
_("nav.catalog", "Продукция", "Products")
_("nav.calculator", "Калькулятор заказа", "Order calculator")
_("nav.marketing", "Маркетинговая поддержка", "Marketing support")
_("nav.prices", "Оптовые цены", "Wholesale prices")
_("cta.become", "Стать дистрибьютором", "Become a distributor")
_("cta.title", "Заберите свой рынок, пока он горячий", "Claim your market while it's hot")
_("cta.text", "Заполните короткую анкету — откроем оптовые цены для вашей страны, а менеджер свяжется с вами в течение рабочего часа.",
  "Fill in a short form — we'll open wholesale prices for your country and a manager will contact you within one business hour.")
_("footer.tagline", "Острые чипсы. Не для слабаков.", "Seriously spicy chips. Not for the faint-hearted.")
_("footer.sections", "Разделы", "Sections")
_("footer.contacts", "Контакты", "Contacts")
_("footer.privacy", "Политика конфиденциальности", "Privacy policy")
_("cookie.text", "Мы используем cookie для аналитики и рекламы, чтобы улучшать сайт.", "We use analytics and advertising cookies to improve the site.")
_("cookie.accept", "Принять", "Accept")
_("cookie.deny", "Только необходимые", "Necessary only")
_("unit.g", "г", "g")
_("unit.kg", "кг", "kg")
_("unit.cm", "см", "cm")
_("unit.m3", "м³", "m³")
_("unit.pcs_box", "шт. в коробке", "packs per box")
_("unit.boxes_short", "кор.", "boxes")

# --- Главная -----------------------------------------------------------------
_("hero.eyebrow", "экспорт от производителя", "export direct from the manufacturer")
_("hero.h1a", "Очень острые.", "Seriously spicy.")
_("hero.h1b", "Не для слабаков!", "Not for the weak!")
_("hero.lead", "MAZZAA — острые и остро-сладкие чипсы, которые разбирают с полки. Ищем дистрибьюторов в странах СНГ и Кавказа: региональные цены в вашей валюте и расчёт заказа за две минуты.",
  "MAZZAA — hot and sweet-and-spicy chips that fly off the shelf. We are looking for distributors across the CIS and the Caucasus: regional prices in your currency and an order quote in two minutes.")
_("fact.sku", "позиций в линейке", "products in the range")
_("fact.weights", "формата упаковки", "pack formats")
_("fact.markets", "стран поставки", "target markets")
_("banner.catalog", "Наша продукция", "Our products")
_("range.title", "Линейка MAZZAA", "The MAZZAA range")
_("range.text", "Четыре формата — от импульсной покупки до упаковки для компании.", "Four formats — from an impulse buy to a sharing pack.")
_("range.all", "Весь каталог", "Full catalogue")
_("depth.word", "ХРУСТ. ОГОНЬ. MAZZAA.", "CRUNCH. FIRE. MAZZAA.")
_("why.title", "Почему дистрибьюторы выбирают MAZZAA", "Why distributors choose MAZZAA")
_("why.text", "Мы строим долгие экспортные партнёрства, а не разовые отгрузки.", "We build long-term export partnerships, not one-off shipments.")
_("why.1.t", "Продукт, который продаёт себя", "A product that sells itself")
_("why.1.d", "Яркая упаковка в форме пламени и вкус, за которым возвращаются: чили, сыр, горчица-васаби, баранина.",
  "Eye-catching flame-shaped packs and a taste people come back for: chili, cheese, mustard-wasabi, lamb.")
_("why.2.t", "Цены для вашей страны", "Prices for your country")
_("why.2.d", "Отдельный прайс-лист в национальной валюте для каждого рынка — без пересчётов и сюрпризов.",
  "A dedicated price list in the national currency of each market — no conversions, no surprises.")
_("why.3.t", "Понятная логистика", "Clear logistics")
_("why.3.d", "Калькулятор сразу показывает вес, объём, паллеты и загрузку 20- и 40-футового контейнера.",
  "The calculator instantly shows weight, volume, pallets and the load of a 20 ft or 40 ft container.")
_("why.4.t", "Маркетинг вместе с вами", "Marketing on your side")
_("why.4.d", "Видео, баннеры для соцсетей, плакаты и материалы для торговых точек — готовы к запуску.",
  "Videos, social media banners, posters and point-of-sale materials — ready to launch.")
_("steps.title", "Как начать работать", "How to get started")
_("steps.1.t", "Заполните анкету", "Fill in the form")
_("steps.1.d", "Страна, компания и контакт — меньше двух минут.", "Country, company and contact — under two minutes.")
_("steps.2.t", "Получите цены", "Get your prices")
_("steps.2.d", "Откроется оптовый прайс для вашей страны и валюты.", "The wholesale price list for your country and currency opens up.")
_("steps.3.t", "Рассчитайте заказ", "Calculate your order")
_("steps.3.d", "Соберите партию: стоимость, вес, объём и контейнеры считаются сами.", "Build your shipment: cost, weight, volume and containers are calculated for you.")
_("steps.4.t", "Отправьте заявку", "Send the request")
_("steps.4.d", "Менеджер согласует договор, оплату и доставку.", "A manager will agree the contract, payment and delivery with you.")
_("markets.title", "Рынки", "Markets")
_("markets.text", "Выберите страну — покажем условия и валюту прайса.", "Choose your country to see the terms and price currency.")

# --- Каталог и товар ---------------------------------------------------------
_("catalog.title", "Продукция MAZZAA", "MAZZAA products")
_("catalog.lead", "Острые и остро-сладкие чипсы в четырёх форматах: 40, 50, 100 и 150 граммов.", "Hot and sweet-and-spicy chips in four formats: 40, 50, 100 and 150 grams.")
_("catalog.price_note", "Оптовые цены открываются после короткой анкеты.", "Wholesale prices open after a short registration form.")
_("spec.pack_weight", "Вес упаковки", "Pack weight")
_("spec.package", "Тип упаковки", "Packaging")
_("spec.packs_box", "Упаковок в коробке", "Packs per box")
_("spec.box_dims", "Габариты коробки", "Box dimensions")
_("spec.gross", "Вес брутто коробки", "Box gross weight")
_("spec.volume", "Объём коробки", "Box volume")
_("spec.pallet", "Коробок на паллете", "Boxes per pallet")
_("spec.tbd", "уточняется", "to be confirmed")
_("product.locked", "Оптовая цена доступна после регистрации", "The wholesale price is available after registration")
_("product.unlock", "Открыть цены", "Unlock prices")
_("product.no_price", "Для вашей страны цена пока не установлена — уточните у менеджера.", "No price is set for your country yet — please ask your manager.")
_("product.to_calc", "В калькулятор", "Add to calculator")
_("product.related", "В этом же формате", "Same format")

# --- Анкета ------------------------------------------------------------------
_("reg.eyebrow", "Анкета дилера", "Dealer application")
_("reg.title", "Стать дистрибьютором MAZZAA", "Become a MAZZAA distributor")
_("reg.lead", "Заполните анкету — и сразу получите доступ к оптовому прайс-листу для вашей страны.", "Fill in the form to get instant access to the wholesale price list for your country.")
_("reg.b1", "Региональные цены в вашей валюте", "Regional prices in your currency")
_("reg.b2", "Калькулятор стоимости, веса и объёма заказа", "Calculator for order cost, weight and volume")
_("reg.b3", "Коммерческое предложение в PDF и Excel", "Commercial offer in PDF and Excel")
_("reg.b4", "Рекламные материалы для вашего рынка", "Marketing materials for your market")
_("reg.consent", "Я согласен(на) на обработку персональных данных.", "I agree to the processing of my personal data.")
_("reg.submit", "Получить оптовые цены", "Get wholesale prices")
_("reg.note", "Мы не передаём ваши данные третьим лицам. Менеджер свяжется с вами в рабочее время.", "We do not share your data with third parties. A manager will contact you during business hours.")
_("form.country", "Страна", "Country")
_("form.city", "Город", "City")
_("form.company", "Название компании", "Company name")
_("form.contact_name", "Контактное лицо", "Contact person")
_("form.phone", "Телефон / WhatsApp", "Phone / WhatsApp")
_("form.email", "Электронная почта", "E-mail")
_("form.activity", "Вид деятельности", "Type of business")
_("form.volume", "Предполагаемый объём закупки", "Expected purchase volume")
_("form.comment", "Комментарий", "Comment")
_("form.choose", "— выберите —", "— select —")
_("form.phone_invalid", "Укажите телефон в международном формате.", "Please enter the phone number in international format.")
_("form.spam", "Не удалось отправить форму. Обновите страницу и попробуйте ещё раз.", "The form could not be sent. Please refresh the page and try again.")
_("activity.distributor", "Дистрибьютор", "Distributor")
_("activity.wholesale", "Оптовая торговля", "Wholesale")
_("activity.retail_chain", "Розничная сеть", "Retail chain")
_("activity.horeca", "HoReCa", "HoReCa")
_("activity.online", "Онлайн-торговля / маркетплейсы", "Online retail / marketplaces")
_("activity.other", "Другое", "Other")
_("volume.trial", "Пробная партия", "Trial batch")
_("volume.lt20", "Меньше 20-футового контейнера", "Less than a 20 ft container")
_("volume.c20", "20-футовый контейнер", "One 20 ft container")
_("volume.c40", "40-футовый контейнер", "One 40 ft container")
_("volume.regular", "Регулярные поставки, несколько контейнеров", "Regular supply, several containers")
_("pending.title", "Анкета получена", "Application received")
_("pending.text", "Спасибо! Менеджер проверит анкету и откроет доступ к оптовым ценам. Мы свяжемся с вами в ближайшее рабочее время.",
  "Thank you! A manager will review your application and open access to wholesale prices. We will contact you during the next business hours.")
_("pending.rejected", "К сожалению, доступ к оптовым ценам сейчас закрыт. Свяжитесь с нами, чтобы уточнить детали.", "Unfortunately, access to wholesale prices is currently closed. Please contact us for details.")

# --- Прайс -------------------------------------------------------------------
_("prices.title", "Оптовый прайс-лист", "Wholesale price list")
_("prices.lead", "Цены за коробку, валюта:", "Prices per box, currency:")
_("prices.empty", "Прайс-лист для вашей страны готовится. Менеджер свяжется с вами и пришлёт цены.", "The price list for your country is being prepared. A manager will contact you with prices.")
_("prices.link_hint", "Ваша персональная ссылка для доступа к ценам с другого устройства:", "Your personal link to access prices from another device:")
_("prices.logout", "Выйти на этом устройстве", "Sign out on this device")
_("col.product", "Продукт", "Product")
_("col.pack_g", "Вес упаковки, г", "Pack weight, g")
_("col.packs_box", "Упаковок в коробке", "Packs per box")
_("col.price_box", "Цена за коробку", "Price per box")
_("col.price_pack", "Цена за упаковку", "Price per pack")
_("col.gross_kg", "Вес брутто, кг", "Gross weight, kg")
_("col.volume_m3", "Объём, м³", "Volume, m³")
_("col.boxes", "Коробок", "Boxes")
_("col.packs", "Упаковок", "Packs")
_("col.amount", "Сумма", "Amount")
_("doc.date", "Дата", "Date")
_("doc.for", "Для", "For")
_("doc.terms", "Условия поставки", "Delivery terms")
_("doc.terms_tbd", "согласуются с менеджером", "to be agreed with the manager")
_("doc.offer", "Коммерческое предложение", "Commercial offer")
_("doc.order", "Заказ", "Order")
_("doc.price_note", "Цены действительны на дату формирования и подтверждаются менеджером при оформлении заказа.", "Prices are valid on the date of issue and are confirmed by the manager when the order is placed.")
_("doc.offer_note", "Предложение не является публичной офертой. Оплата, договор и доставка согласуются с менеджером.", "This offer is not a public offer. Payment, contract and delivery are agreed with the manager.")

# --- Калькулятор -------------------------------------------------------------
_("calc.title", "Калькулятор оптового заказа", "Wholesale order calculator")
_("calc.lead", "Укажите количество коробок — стоимость, вес, объём и загрузка контейнера посчитаются автоматически.", "Enter the number of boxes — cost, weight, volume and container load are calculated automatically.")
_("calc.locked", "Вес и объём считаются уже сейчас. Чтобы увидеть цены и отправить заказ, заполните анкету.", "Weight and volume are calculated right away. To see prices and send an order, fill in the form.")
_("calc.price_hidden", "цена после анкеты", "price after registration")
_("calc.your", "Ваш заказ", "Your order")
_("calc.empty", "Добавьте товары — расчёт появится здесь.", "Add products — the calculation will appear here.")
_("calc.total", "Итого", "Total")
_("calc.weight", "Общий вес брутто", "Total gross weight")
_("calc.volume", "Общий объём", "Total volume")
_("calc.pallets", "Паллет", "Pallets")
_("calc.container", "Контейнер", "Container")
_("calc.fill", "загрузка", "load")
_("calc.disclaimer", "Расчёт загрузки предварительный: окончательную загрузку подтверждает менеджер по логистике.", "The load estimate is preliminary: final loading is confirmed by the logistics manager.")
_("calc.comment", "Комментарий к заказу (необязательно)", "Order comment (optional)")
_("calc.send", "Отправить заказ", "Send order")
_("calc.offer", "Коммерческое предложение", "Commercial offer")
_("calc.register_to_send", "Заполнить анкету и увидеть цены", "Register to see prices")
_("calc.clear", "Очистить расчёт", "Clear calculation")
_("calc.remove", "Удалить", "Remove")
_("calc.partial", "часть данных уточняется", "some data to be confirmed")
_("calc.pcs", "шт.", "pcs")
_("done.number", "Заказ №", "Order No.")
_("done.title", "Заказ отправлен", "Order sent")
_("done.text", "Спасибо! Менеджер свяжется с вами, чтобы согласовать договор, оплату и доставку.", "Thank you! A manager will contact you to agree the contract, payment and delivery.")

# --- Маркетинг ---------------------------------------------------------------
_("mkt.title", "Маркетинговая поддержка дистрибьюторов", "Marketing support for distributors")
_("mkt.lead", "Мы помогаем продавать: готовые рекламные материалы и совместные акции для вашего рынка.", "We help you sell: ready-made advertising materials and joint promotions for your market.")
_("mkt.1.t", "Видео и фото", "Video and photo")
_("mkt.1.d", "Рекламные ролики и профессиональные фотографии продукции.", "Commercials and professional product photography.")
_("mkt.2.t", "Соцсети", "Social media")
_("mkt.2.d", "Готовые баннеры для Instagram и Facebook под ваш язык.", "Ready-made Instagram and Facebook banners in your language.")
_("mkt.3.t", "Торговые точки", "Point of sale")
_("mkt.3.d", "Плакаты, воблеры и стойки для магазинов.", "Posters, wobblers and display stands for shops.")
_("mkt.4.t", "Акции", "Promotions")
_("mkt.4.d", "Совместные маркетинговые акции и поддержка запуска на рынке.", "Joint promotions and market launch support.")
_("mkt.kind.video", "Рекламные видеоролики", "Commercials")
_("mkt.kind.photo", "Фотографии продукции", "Product photos")
_("mkt.kind.social", "Баннеры для Instagram и Facebook", "Instagram and Facebook banners")
_("mkt.kind.poster", "Плакаты для магазинов", "Shop posters")
_("mkt.kind.pos", "Материалы для торговых точек", "Point-of-sale materials")
_("mkt.kind.promo", "Маркетинговые акции", "Promotions")
_("mkt.kind.terms", "Условия маркетинговой поддержки", "Marketing support terms")
_("mkt.watch", "Смотреть", "Watch")
_("mkt.download", "Скачать", "Download")
_("mkt.soon", "Материалы скоро появятся. Зарегистрируйтесь — мы сообщим, когда библиотека будет готова.", "Materials are coming soon. Register and we will let you know when the library is ready.")

# --- Посадочные страницы -----------------------------------------------------
_("market.h1", "Острые чипсы MAZZAA оптом —", "MAZZAA spicy chips wholesale —")
_("market.lead", "Прямые поставки от производителя. Отдельный прайс-лист в национальной валюте, расчёт партии онлайн и маркетинговая поддержка для дистрибьюторов.",
  "Direct supply from the manufacturer. A dedicated price list in the national currency, online shipment calculation and marketing support for distributors.")
_("market.cta", "Получить цены в", "Get prices in")

# --- Политика ----------------------------------------------------------------
_("privacy.p1", "Оператор персональных данных — QOSIMOV GROUP (Узбекистан). Мы обрабатываем данные, которые вы указываете в анкете дилера и при оформлении заказа: страна, город, компания, контактное лицо, телефон, e-mail, комментарии.",
  "The personal data controller is QOSIMOV GROUP (Uzbekistan). We process the data you provide in the dealer form and when placing an order: country, city, company, contact person, phone, e-mail and comments.")
_("privacy.p2", "Цель обработки — рассмотрение заявки на сотрудничество, предоставление оптовых цен, обработка заказов и связь с вами. Данные хранятся в нашей CRM-системе и не передаются третьим лицам, кроме случаев, предусмотренных законом.",
  "The purpose of processing is to review your partnership request, provide wholesale prices, process orders and contact you. The data is stored in our CRM system and is not shared with third parties except as required by law.")
_("privacy.p3", "Вы можете запросить уточнение или удаление своих данных, написав нам по контактам, указанным на сайте.",
  "You may request correction or deletion of your data by contacting us using the details on this site.")
_("privacy.p4", "Отправляя анкету, вы подтверждаете согласие на обработку персональных данных на этих условиях.",
  "By submitting the form you consent to the processing of your personal data under these terms.")
_("privacy.cookies", "Необходимые cookie обеспечивают работу сайта (язык, доступ к ценам, защита форм). Аналитические и рекламные cookie (Google Analytics, Google Ads, Meta Pixel) включаются только с вашего согласия.",
  "Necessary cookies keep the site working (language, price access, form protection). Analytics and advertising cookies (Google Analytics, Google Ads, Meta Pixel) are enabled only with your consent.")
_("privacy.cookie_reset", "Изменить выбор cookie", "Change cookie choice")

_cache = {"at": 0.0, "data": {}}


def invalidate():
    _cache["at"] = 0.0


def _overrides():
    if time.time() - _cache["at"] > 30:
        from .models import UiText
        codes = [code for code, _name in settings.LANGUAGES]
        data = {}
        for row in UiText.objects.values("key", *[f"text_{c}" for c in codes]):
            data[row["key"]] = {c: row[f"text_{c}"] for c in codes if row[f"text_{c}"]}
        _cache.update(at=time.time(), data=data)
    return _cache["data"]


def t(key, lang=None):
    lang = (lang or get_language() or settings.LANGUAGE_CODE)[:2]
    custom = _overrides().get(key, {})
    default = S.get(key, {})
    return custom.get(lang) or default.get(lang) or custom.get("en") or default.get("en") or default.get("ru") or key


def sync_keys():
    """Создаёт в базе пустые записи для всех ключей, чтобы их можно было править в админке."""
    from .models import UiText
    existing = set(UiText.objects.values_list("key", flat=True))
    UiText.objects.bulk_create([UiText(key=k) for k in S if k not in existing])
