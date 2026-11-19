from django.contrib import admin, messages
from django.utils import timezone

from . import services
from .models import CrmJob


@admin.register(CrmJob)
class CrmJobAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "dealer", "order", "status", "attempts", "next_attempt_at", "short_error")
    list_filter = ("status", "kind")
    search_fields = ("dealer__company", "dealer__phone", "order__number")
    readonly_fields = [f.name for f in CrmJob._meta.fields]
    actions = ["retry"]

    @admin.display(description="Ошибка")
    def short_error(self, obj):
        return obj.last_error[:90]

    @admin.action(description="Повторить передачу в Bitrix24 сейчас")
    def retry(self, request, queryset):
        ok = 0
        for job in queryset.exclude(status=CrmJob.DONE):
            job.status, job.next_attempt_at = CrmJob.PENDING, timezone.now()
            ok += services.run_job(job).status == CrmJob.DONE
        messages.info(request, f"Успешно передано: {ok} из {queryset.count()}")

    def has_add_permission(self, request):
        return False
