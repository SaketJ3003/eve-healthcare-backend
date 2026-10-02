from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from bookings.models import Booking
from .models import Payment

from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer
)
from .services import process_payment, process_payment_webhook


@extend_schema(
    request=PaymentCreateSerializer,
    responses=PaymentSerializer,
)
class PaymentCreateView(APIView):    
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PaymentCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        payment = process_payment(
            user=request.user,
            booking_id=serializer.validated_data[
                "booking_id"
            ],
            force_status=serializer.validated_data.get(
                "simulated_status"
            ),
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    responses=PaymentSerializer,
)
class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(
            Payment.objects.select_related("booking"),
            id=pk,
            booking__user=request.user,
        )

        return Response(
            PaymentSerializer(payment).data
        )


@extend_schema(
    request=PaymentWebhookSerializer,
    responses={
        200: dict,
        404: dict,
    },
)
class PaymentWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PaymentWebhookSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:
            result = process_payment_webhook(
                event_id=data["event_id"],
                event_type=data["event_type"],
                payment_id=data["payment_id"],
                status=data["status"],
                payload=request.data,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Payment not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if result["duplicate"]:
            return Response(
                {
                    "detail": (
                        "Webhook already processed."
                    ),
                    "event_id": data["event_id"],
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Webhook processed successfully.",
                "event_id": data["event_id"],
            },
            status=status.HTTP_200_OK,
        )