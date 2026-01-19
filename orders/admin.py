from django.contrib import admin
from .models import Order, OrderItem
from django.core.exceptions import ValidationError
from orders.services.order_service import OrderService

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_at_time")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    ordering = ("-created_at",)

    inlines = [OrderItemInline]

    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        """
        Enforce status transition rules even in admin.
        """
        if change:
            old_obj = Order.objects.get(pk=obj.pk)

            if old_obj.status != obj.status:
                try:
                    OrderService.admin_update_status(
                        admin_user=request.user,
                        order_id=obj.pk,
                        new_status=obj.status,
                    )
                    return  # service already saved
                except Exception as e:
                    raise ValidationError(str(e))

        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price_at_time",
    )

    readonly_fields = (
        "order",
        "product",
        "quantity",
        "price_at_time",
    )
