from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from core import i18n
from core.documents import file_response
from core.models import SiteSettings
from dealers.access import current_dealer

from .models import Price, Product, WeightCategory


def catalog(request):
    products = Product.objects.filter(is_active=True).select_related("flavor", "weight")
    weights = list(WeightCategory.objects.all())
    for w in weights:
        w.items = [p for p in products if p.weight_id == w.pk]
    return render(request, "catalog.html", {"weights": [w for w in weights if w.items]})


def product(request, slug):
    p = get_object_or_404(Product.objects.select_related("flavor", "weight"), slug=slug, is_active=True)
    dealer = current_dealer(request)
    price = None
    if dealer and dealer.has_access:
        price = Price.objects.filter(product=p, country=dealer.country, is_hidden=False).first()
    related = Product.objects.filter(is_active=True, weight=p.weight).exclude(pk=p.pk).select_related("flavor", "weight")[:4]
    return render(request, "product.html", {"p": p, "price": price, "related": related})


def _price_rows(country):
    return list(
        Price.objects.filter(country=country, is_hidden=False, product__is_active=True)
        .select_related("product__weight", "product__flavor")
        .order_by("product__weight__grams", "product__sort", "product_id")
    )


def _gate(request):
    """Возвращает (dealer, redirect). Прайс виден только дилеру с открытым доступом."""
    dealer = current_dealer(request)
    if not dealer:
        return None, redirect(f"{reverse('register')}?next={request.path}")
    if not dealer.has_access:
        return None, redirect("pending")
    return dealer, None


def prices(request):
    dealer, response = _gate(request)
    if response:
        return response
    return render(request, "prices.html", {"rows": _price_rows(dealer.country), "country": dealer.country})


def prices_download(request, fmt):
    dealer, response = _gate(request)
    if response:
        return response
    s = SiteSettings.load()
    t = i18n.t
    country = dealer.country
    rows = []
    for n, price in enumerate(_price_rows(country), start=1):
        p = price.product
        per_pack = round(price.price / p.packs_per_box, 2) if p.packs_per_box else None
        rows.append([n, p.name, p.weight.grams, p.packs_per_box, price.price, per_pack,
                     p.gross_weight_kg, p.volume_m3])
    doc = {
        "title": f"{s.brand_name} — {t('prices.title')}: {country.name} ({country.currency.code})",
        "meta": [f"{t('doc.date')}: {timezone.localdate():%d.%m.%Y}",
                 f"{t('doc.for')}: {dealer.company}, {dealer.city}",
                 f"{t('doc.terms')}: {s.price_terms or t('doc.terms_tbd')}"],
        "headers": ["№", t("col.product"), t("col.pack_g"), t("col.packs_box"),
                    f"{t('col.price_box')}, {country.currency.code}", f"{t('col.price_pack')}, {country.currency.code}",
                    t("col.gross_kg"), t("col.volume_m3")],
        "rows": rows,
        "notes": [t("doc.price_note"), f"{s.company_name} · {s.phone} · {s.email}"],
    }
    return file_response(doc, fmt, f"mazzaa-price-{country.code}-{timezone.localdate():%Y%m%d}")
