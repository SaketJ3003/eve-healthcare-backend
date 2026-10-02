from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from diagnostics.models import DiagnosticCentre, DiagnosticTest


class BookingStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    centre = models.ForeignKey(
        DiagnosticCentre,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    test = models.ForeignKey(
        DiagnosticTest,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    appointment_datetime = models.DateTimeField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["appointment_datetime"]),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"