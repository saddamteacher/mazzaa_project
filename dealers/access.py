from .models import Dealer


def current_dealer(request):
    """Дилер, привязанный к сессии браузера (или None)."""
    if not hasattr(request, "_dealer"):
        dealer_id = request.session.get("dealer_id") if hasattr(request, "session") else None
        request._dealer = (
            Dealer.objects.select_related("country__currency").filter(pk=dealer_id).first() if dealer_id else None
        )
    return request._dealer


def login_dealer(request, dealer):
    request.session.cycle_key()
    request.session["dealer_id"] = dealer.pk
    request._dealer = dealer


def push_event(request, name, **params):
    """Событие аналитики, которое отправится на следующей странице (после редиректа)."""
    request.session["track"] = request.session.get("track", []) + [{"event": name, **params}]
