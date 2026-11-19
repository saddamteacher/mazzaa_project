from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import MarketingMaterial


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(TabbedTranslationAdmin):
    list_display = ("title", "kind", "dealers_only", "is_active", "sort")
    list_editable = ("dealers_only", "is_active", "sort")
    list_filter = ("kind", "is_active")
