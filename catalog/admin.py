from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Country, Currency, Flavor, Price, PriceHistory, Product, ProductImage, WeightCategory


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol")


@admin.register(Country)
class CountryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "code", "currency", "is_active", "landing_enabled", "bitrix_responsible_id", "sort")
    list_editable = ("currency", "is_active", "landing_enabled", "bitrix_responsible_id", "sort")


@admin.register(WeightCategory)
class WeightAdmin(TabbedTranslationAdmin):
    list_display = ("grams", "package_note", "sort")


@admin.register(Flavor)
class FlavorAdmin(TabbedTranslationAdmin):
    list_display = ("name", "color", "heat", "sort")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class PriceInline(admin.TabularInline):
    model = Price
    extra = 0
    fields = ("country", "price", "is_hidden")


class PriceUserMixin:
    """Запоминает, кто изменил цену, — попадает в историю цен."""

    def save_model(self, request, obj, form, change):
        obj._changed_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for obj in formset.save(commit=False):
            obj._changed_by = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(Product)
class ProductAdmin(PriceUserMixin, TabbedTranslationAdmin):
    list_display = ("name", "weight", "flavor", "packs_per_box", "gross_weight_kg", "volume_m3", "is_active", "sort")
    list_editable = ("is_active", "sort")
    list_filter = ("weight", "flavor", "is_active")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, PriceInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "sku", "flavor", "weight", "description", "image", "is_active", "sort")}),
        ("Логистика коробки", {"fields": (
            "packs_per_box", ("box_length_cm", "box_width_cm", "box_height_cm"),
            "gross_weight_kg", "volume_m3", "boxes_per_pallet")}),
    )


@admin.register(Price)
class PriceAdmin(PriceUserMixin, admin.ModelAdmin):
    """Прайс-листы: выберите страну в фильтре справа и правьте цены прямо в списке."""

    list_display = ("product", "country", "currency", "price", "is_hidden", "updated_at")
    list_editable = ("price", "is_hidden")
    list_filter = ("country", "product__weight", "is_hidden")
    search_fields = ("product__name",)
    list_select_related = ("product", "product__weight", "country", "country__currency")
    list_per_page = 100

    @admin.display(description="Валюта")
    def currency(self, obj):
        return obj.country.currency.code


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("changed_at", "product", "country", "old_price", "new_price", "is_hidden", "changed_by")
    list_filter = ("country", "changed_by")
    date_hierarchy = "changed_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
