from rest_framework import serializers

from bookings.models import Booking
from .models import Payment, PaymentStatus


class PaymentCreateSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(min_value=1)

    simulated_status = serializers.ChoiceField(
        choices=[
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
        ],
        required=False,
    )

    def validate_booking_id(self, value):
        user = self.context["request"].user

        try:
            booking = Booking.objects.get(
                id=value,
                user=user,
            )
        except Booking.DoesNotExist:
            raise serializers.ValidationError(
                "Booking not found."
            )

        if booking.status != "PENDING":
            raise serializers.ValidationError(
                "Payment can only be initiated for a pending booking."
            )

        return value


class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(
        source="booking.id",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "booking_id",
            "provider_payment_id",
            "amount",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields



class PaymentWebhookSerializer(serializers.Serializer):
    event_id = serializers.CharField(
        max_length=255
    )
    event_type = serializers.CharField(
        max_length=100
    )
    payment_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=[
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
        ]
    )