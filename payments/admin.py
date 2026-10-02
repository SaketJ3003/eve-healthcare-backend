from django.contrib import admin

from .models import Payment, PaymentWebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "provider_payment_id",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("provider_payment_id",)


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_id",
        "payment",
        "event_type",
        "status",
        "processed_at",
    )
    search_fields = ("event_id",)