from modeltranslation.translator import TranslationOptions, register

from .models import Banner, SiteSettings, UiText


@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = ("about_title", "about_text", "address", "privacy_text", "price_terms")


@register(Banner)
class BannerTR(TranslationOptions):
    fields = ("title", "subtitle")


@register(UiText)
class UiTextTR(TranslationOptions):
    fields = ("text",)
