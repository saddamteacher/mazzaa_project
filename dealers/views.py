import time

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone, translation
from django.utils.http import url_has_allowed_host_and_scheme

from catalog.models import Country
from core.i18n import t
from core.models import SiteSettings
from crm import services
from crm.models import CrmJob

from .access import current_dealer, login_dealer, push_event
from .forms import DealerForm
from .models import Dealer, normalize_phone


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR")


def spam_error(request, form):
    """Ловушка, слишком быстрая отправка или превышение лимита с одного IP."""
    if form.data.get("website"):
        return True
    try:
        stamp = signing.loads(form.data.get("ts", ""), max_age=60 * 60 * 12)["t"]
    except (signing.BadSignature, KeyError, TypeError):
        return True
    if time.time() - stamp < settings.FORM_MIN_SECONDS:
        return True
    key = f"reg:{client_ip(request)}"
    count = cache.get(key, 0)
    if count >= settings.FORM_RATE_LIMIT:
        return True
    cache.set(key, count + 1, 3600)
    return False


def _next_url(request, default):
    url = request.POST.get("next") or request.GET.get("next") or ""
    if url and url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()}):
        return url
    return default


def register(request):
    dealer = current_dealer(request)
    if dealer and request.method == "GET":
        return redirect("prices" if dealer.has_access else "pending")

    initial = {}
    code = request.GET.get("country")
    if code:
        initial["country"] = Country.objects.filter(code=code.lower(), is_active=True).first()
    form = DealerForm(request.POST or None, initial=initial)

    if request.method == "POST":
        if spam_error(request, form):
            form.add_error(None, t("form.spam"))
        elif form.is_valid():
            s = SiteSettings.load()
            data = {k: v for k, v in form.cleaned_data.items() if k not in ("consent", "website", "ts")}
            digits = normalize_phone(data["phone"])
            dealer = Dealer.objects.filter(phone_digits=digits).first()
            is_new = dealer is None
            if is_new:
                dealer = Dealer(status=Dealer.APPROVED if s.price_access_mode == s.ACCESS_AUTO else Dealer.PENDING,
                                **request.session.get("attribution", {}))
            for key, value in data.items():
                setattr(dealer, key, value)
            dealer.language = translation.get_language() or "ru"
            dealer.ip = client_ip(request)
            dealer.consent_at = timezone.now()
            dealer.save()
            login_dealer(request, dealer)
            if is_new or not dealer.bitrix_lead_id:
                # Лид создаётся сразу, даже если клиент ещё не оформил заказ.
                if not dealer.crm_jobs.filter(kind=CrmJob.LEAD).exclude(status=CrmJob.DONE).exists():
                    services.enqueue(CrmJob.LEAD, dealer)
            push_event(request, "generate_lead", country=dealer.country.code)
            return redirect(_next_url(request, "prices") if dealer.has_access else "pending")

    return render(request, "register.html", {"form": form, "next": _next_url(request, "")})


def pending(request):
    dealer = current_dealer(request)
    if not dealer:
        return redirect("register")
    if dealer.has_access:
        return redirect("prices")
    return render(request, "pending.html")


def access_link(request, token):
    """Персональная ссылка дилера: восстанавливает доступ на другом устройстве."""
    dealer = get_object_or_404(Dealer, token=token)
    login_dealer(request, dealer)
    return redirect("prices" if dealer.has_access else "pending")


def logout(request):
    if request.method == "POST":
        request.session.pop("dealer_id", None)
    return redirect("home")
