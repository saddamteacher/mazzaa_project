from modeltranslation.translator import TranslationOptions, register

from .models import Country, Flavor, Product, WeightCategory


@register(Country)
class CountryTR(TranslationOptions):
    fields = ("name", "landing_title", "landing_text")


@register(WeightCategory)
class WeightTR(TranslationOptions):
    fields = ("package_note",)


@register(Flavor)
class FlavorTR(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTR(TranslationOptions):
    fields = ("name", "description")
