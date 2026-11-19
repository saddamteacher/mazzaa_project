UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")


class UtmMiddleware:
    """Запоминает рекламный источник первого визита (UTM, gclid/fbclid, реферер) в сессии."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        params = request.GET
        has_marks = any(k in params for k in UTM_KEYS + ("gclid", "fbclid"))
        if request.method == "GET" and (has_marks or "attribution" not in request.session):
            if has_marks or not request.path.startswith(("/static/", "/media/", "/api/")):
                data = {k: params.get(k, "")[:200] for k in UTM_KEYS}
                data["click_id"] = (params.get("gclid") or params.get("fbclid") or "")[:300]
                data["referrer"] = request.META.get("HTTP_REFERER", "")[:500]
                data["landing_page"] = request.get_full_path()[:500]
                request.session["attribution"] = data
        return self.get_response(request)
