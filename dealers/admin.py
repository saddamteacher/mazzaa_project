from django.contrib import admin

from crm.models import CrmJob

from .models import Dealer


class CrmJobInline(admin.TabularInline):
    model = CrmJob
    extra = 0
    can_delete = False
    fields = ("kind", "order", "status", "attempts", "last_error", "done_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ("created_at", "company", "contact_name", "phone", "country", "city", "status",
                    "utm_source", "bitrix_lead_id")
    list_filter = ("status", "country", "activity", "utm_source", "language")
    search_fields = ("company", "contact_name", "phone", "email", "city")
    date_hierarchy = "created_at"
    readonly_fields = ("token", "bitrix_lead_id", "bitrix_task_id", "task_deadline", "overdue_notified",
                       "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "click_id",
                       "referrer", "landing_page", "ip", "consent_at", "created_at")
    inlines = [CrmJobInline]
    actions = ["approve", "reject"]

    @admin.action(description="Открыть доступ к ценам")
    def approve(self, request, queryset):
        queryset.update(status=Dealer.APPROVED)

    @admin.action(description="Закрыть доступ к ценам")
    def reject(self, request, queryset):
        queryset.update(status=Dealer.REJECTED)
