from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path

from catalog import views as catalog
from core import views as core
from dealers import views as dealers
from marketing import views as marketing
from orders import views as orders

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("robots.txt", core.robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": core.SITEMAPS}, name="sitemap"),
    path("api/calc/", orders.api_calc, name="api_calc"),
    re_path(r"^media/(?P<path>.*)$", core.media),
]

urlpatterns += i18n_patterns(
    path("", core.home, name="home"),
    path("catalog/", catalog.catalog, name="catalog"),
    path("catalog/<slug:slug>/", catalog.product, name="product"),
    path("become-distributor/", dealers.register, name="register"),
    path("become-distributor/pending/", dealers.pending, name="pending"),
    path("access/<uuid:token>/", dealers.access_link, name="access_link"),
    path("logout/", dealers.logout, name="logout"),
    path("prices/", catalog.prices, name="prices"),
    path("prices/download.<str:fmt>", catalog.prices_download, name="prices_download"),
    path("calculator/", orders.calculator, name="calculator"),
    path("calculator/offer.<str:fmt>", orders.offer, name="offer"),
    path("order/submit/", orders.submit, name="order_submit"),
    path("order/<str:number>/", orders.order_done, name="order_done"),
    path("order/<str:number>/offer.<str:fmt>", orders.order_offer, name="order_offer"),
    path("marketing/", marketing.marketing, name="marketing"),
    path("marketing/download/<int:pk>/", marketing.download, name="marketing_download"),
    path("markets/<slug:code>/", core.market, name="market"),
    path("privacy/", core.privacy, name="privacy"),
)
