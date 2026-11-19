from django.contrib import admin
from django.contrib.admin.models import LogEntry
from modeltranslation.admin import TabbedTranslationAdmin

from . import i18n
from .models import Banner, SiteSettings, UiText

admin.site.site_header = "MAZZAA — управление сайтом"
admin.site.site_title = "MAZZAA"
admin.site.index_title = "Панель администратора"


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ("Бренд и компания", {"fields": ("brand_name", "logo", "hero_video", "company_name", "about_title", "about_text")}),
        ("Контакты", {"fields": ("address", "phone", "email", "whatsapp", "telegram", "instagram", "facebook")}),
        ("Цены", {"fields": ("price_access_mode", "price_terms")}),
        ("Аналитика и реклама", {"fields": (
            "gtm_id", "ga4_id", "google_ads_id", "google_ads_lead_label", "google_ads_order_label",
            "meta_pixel_id", "gsc_verification")}),
        ("Bitrix24: регламент", {"fields": (
            "bitrix_default_responsible_id", "bitrix_head_id", "reaction_minutes",
            ("work_start", "work_end"), "work_days")}),
        ("Юридическое", {"fields": ("privacy_text",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(TabbedTranslationAdmin):
    list_display = ("title", "link", "theme", "is_active", "sort")
    list_editable = ("is_active", "sort")


@admin.register(UiText)
class UiTextAdmin(TabbedTranslationAdmin):
    list_display = ("key", "default_ru", "text_ru", "text_en")
    search_fields = ("key", "text_ru", "text_en")
    readonly_fields = ("key", "default_ru", "default_en")
    fields = ("key", "default_ru", "default_en", "text")

    @admin.display(description="По умолчанию (RU)")
    def default_ru(self, obj):
        return i18n.STRINGS.get(obj.key, {}).get("ru", "")

    @admin.display(description="По умолчанию (EN)")
    def default_en(self, obj):
        return i18n.STRINGS.get(obj.key, {}).get("en", "")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Журнал важных изменений: кто, когда и что менял в админ-панели."""

    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag", "change_message")
    list_filter = ("user", "content_type", "action_flag")
    date_hierarchy = "action_time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
