from django.conf import settings

from dealers.access import current_dealer

from .models import SiteSettings


def site(request):
    dealer = current_dealer(request)
    s = SiteSettings.load()
    return {
        "site": s,
        "analytics": {"gtm": s.gtm_id, "ga4": s.ga4_id, "ads": s.google_ads_id, "adsLead": s.google_ads_lead_label,
                      "adsOrder": s.google_ads_order_label, "pixel": s.meta_pixel_id},
        "dealer": dealer,
        "has_access": bool(dealer and dealer.has_access),
        "LANGS": settings.LANGUAGES,
        "track_events": request.session.pop("track", []) if hasattr(request, "session") else [],
    }
