from rest_framework import serializers

from .models import DiagnosticCentre, DiagnosticTest


class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        fields = (
            "id",
            "centre",
            "name",
            "description",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Price cannot be negative."
            )

        return value


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    tests = DiagnosticTestSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = DiagnosticCentre
        fields = (
            "id",
            "name",
            "location",
            "is_active",
            "tests",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "tests",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Centre name cannot be empty."
            )

        return value