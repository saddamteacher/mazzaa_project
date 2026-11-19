from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dealers.access import current_dealer

from .models import MarketingMaterial


def marketing(request):
    materials = list(MarketingMaterial.objects.filter(is_active=True))
    groups = [(key, [m for m in materials if m.kind == key]) for key, _ in MarketingMaterial.KINDS]
    return render(request, "marketing.html", {"groups": groups, "has_materials": bool(materials)})


def download(request, pk):
    m = get_object_or_404(MarketingMaterial, pk=pk, is_active=True)
    if not m.file:
        raise Http404
    if m.dealers_only and not current_dealer(request):
        return redirect(f"{reverse('register')}?next={reverse('marketing')}")
    return FileResponse(m.file.open("rb"), as_attachment=True, filename=m.file.name.rsplit("/", 1)[-1])
