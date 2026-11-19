from django import template
from django.urls import translate_url
from django.utils.safestring import mark_safe

from core import i18n

register = template.Library()


@register.simple_tag
def t(key, **kwargs):
    text = i18n.t(key)
    return text.format(**kwargs) if kwargs else text


@register.simple_tag(takes_context=True)
def lang_url(context, code):
    """Адрес текущей страницы на другом языке."""
    request = context["request"]
    return translate_url(request.get_full_path(), code)


@register.filter
def num(value, digits=0):
    """1234567.5 -> «1 234 567,5» (неразрывные пробелы как разделитель тысяч)."""
    if value is None or value == "":
        return "—"
    text = f"{float(value):,.{int(digits)}f}".replace(",", " ")
    return text


@register.inclusion_tag("_pack.html")
def pack(product, size="md"):
    return {"p": product, "size": size}


@register.simple_tag
def heat(level):
    return mark_safe("".join(
        f'<i class="pepper{" on" if i < level else ""}"></i>' for i in range(5)))


@register.simple_tag(takes_context=True)
def local_link(context, link):
    """Внутренняя ссылка из админки (/catalog/) -> с префиксом текущего языка (/ru/catalog/)."""
    from django.conf import settings
    lang = context["request"].LANGUAGE_CODE
    codes = [c for c, _n in settings.LANGUAGES]
    if link.startswith("/") and not link.startswith("//") and link.split("/")[1] not in codes:
        return f"/{lang}{link}"
    return link
