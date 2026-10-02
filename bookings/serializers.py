from django.utils import timezone
from rest_framework import serializers

from diagnostics.models import DiagnosticCentre, DiagnosticTest

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        source="user.username"
    )

    centre_name = serializers.ReadOnlyField(
        source="centre.name"
    )

    test_name = serializers.ReadOnlyField(
        source="test.name"
    )

    class Meta:
        model = Booking
        fields = (
            "id",
            "user",
            "centre",
            "centre_name",
            "test",
            "test_name",
            "appointment_datetime",
            "amount",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "amount",
            "status",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        centre = attrs["centre"]
        test = attrs["test"]
        appointment_datetime = attrs[
            "appointment_datetime"
        ]

        if not centre.is_active:
            raise serializers.ValidationError(
                {
                    "centre": (
                        "This diagnostic centre is not active."
                    )
                }
            )

        if not test.is_active:
            raise serializers.ValidationError(
                {
                    "test": (
                        "This diagnostic test is not active."
                    )
                }
            )

        if test.centre_id != centre.id:
            raise serializers.ValidationError(
                {
                    "test": (
                        "The selected test does not "
                        "belong to the selected centre."
                    )
                }
            )

        if appointment_datetime <= timezone.now():
            raise serializers.ValidationError(
                {
                    "appointment_datetime": (
                        "Appointment must be in the future."
                    )
                }
            )

        return attrs