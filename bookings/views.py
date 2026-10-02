from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Booking, BookingStatus
from .serializers import BookingSerializer
from .services import create_booking


@extend_schema_view(
    retrieve=extend_schema(
        description="Retrieve one booking belonging to the authenticated user."
    ),
)
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related(
                "user",
                "centre",
                "test",
            )
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data

        booking = create_booking(
            user=self.request.user,
            centre=validated_data["centre"],
            test=validated_data["test"],
            appointment_datetime=(
                validated_data["appointment_datetime"]
            ),
        )

        serializer.instance = booking

    @action(
        detail=True,
        methods=["post"],
    )
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == BookingStatus.CANCELLED:
            return Response(
                {
                    "detail": (
                        "Booking is already cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.status != BookingStatus.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending bookings can "
                        "be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = BookingStatus.CANCELLED
        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            BookingSerializer(booking).data
        )