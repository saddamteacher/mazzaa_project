from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "name", "boxes", "price", "amount")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "created_at", "dealer", "country", "total_amount", "currency", "total_boxes", "crm_status")
    list_filter = ("country", "currency")
    search_fields = ("number", "dealer__company", "dealer__phone")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in Order._meta.fields]
    inlines = [OrderItemInline]

    @admin.display(description="Bitrix24")
    def crm_status(self, obj):
        job = obj.crm_jobs.first()
        return job.get_status_display() if job else "—"

    def has_add_permission(self, request):
        return False
