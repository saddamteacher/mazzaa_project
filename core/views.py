from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.static import serve

from catalog.models import Country, Product, WeightCategory

from .models import Banner


def home(request):
    return render(request, "home.html", {
        "banners": Banner.objects.filter(is_active=True)[:3],
        "weights": WeightCategory.objects.all(),
        "featured": Product.objects.filter(is_active=True).select_related("flavor", "weight")[:8],
        "markets": Country.objects.filter(is_active=True).select_related("currency"),
    })


def market(request, code):
    """Посадочная страница под рекламу на конкретную страну."""
    country = get_object_or_404(Country, code=code, is_active=True, landing_enabled=True)
    return render(request, "market.html", {
        "country": country,
        "featured": Product.objects.filter(is_active=True, prices__country=country, prices__is_hidden=False)
        .select_related("flavor", "weight")[:8]
        or Product.objects.filter(is_active=True).select_related("flavor", "weight")[:8],
    })


def privacy(request):
    return render(request, "privacy.html")


def robots_txt(request):
    base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
    lines = ["User-agent: *", f"Disallow: /{settings.ADMIN_URL}", "Disallow: /api/", "Disallow: /media/protected/",
             "Disallow: /*/prices/", "Disallow: /*/access/", "", f"Sitemap: {base}/sitemap.xml"]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def media(request, path):
    """Отдаёт загруженные файлы. Папка protected/ доступна только через проверяющие доступ страницы."""
    if path.startswith("protected/"):
        raise Http404
    return serve(request, path, document_root=settings.MEDIA_ROOT)


class StaticSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "weekly"

    def items(self):
        return ["home", "catalog", "calculator", "marketing", "register", "privacy"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    i18n = True
    alternates = True
    changefreq = "weekly"

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, item):
        return reverse("product", args=[item.slug])


class MarketSitemap(Sitemap):
    i18n = True
    alternates = True

    def items(self):
        return Country.objects.filter(is_active=True, landing_enabled=True)

    def location(self, item):
        return reverse("market", args=[item.code])


SITEMAPS = {"static": StaticSitemap, "products": ProductSitemap, "markets": MarketSitemap}
