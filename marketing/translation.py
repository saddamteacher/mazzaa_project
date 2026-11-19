from modeltranslation.translator import TranslationOptions, register

from .models import MarketingMaterial


@register(MarketingMaterial)
class MarketingMaterialTR(TranslationOptions):
    fields = ("title", "description")
