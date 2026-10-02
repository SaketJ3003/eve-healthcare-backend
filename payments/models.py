import uuid

from django.core.validators import MinValueValidator
from django.db import models

from bookings.models import Booking


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"


class Payment(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name="payment",
    )
    provider_payment_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.provider_payment_id}"


class PaymentWebhookEvent(models.Model):
    event_id = models.CharField(
        max_length=255,
        unique=True,
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="webhook_events",
    )
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    processed_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.event_id