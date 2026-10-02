from datetime import timedelta
import uuid

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus
from diagnostics.models import (
    DiagnosticCentre,
    DiagnosticTest,
)

from .models import (
    Payment,
    PaymentStatus,
    PaymentWebhookEvent,
)


@pytest.fixture
def user():
    return User.objects.create_user(
        username="customer",
        password="Password123",
    )


@pytest.fixture
def centre():
    return DiagnosticCentre.objects.create(
        name="EVE Diagnostics",
        location="Jaipur",
    )


@pytest.fixture
def test(centre):
    return DiagnosticTest.objects.create(
        centre=centre,
        name="CBC",
        price="500.00",
    )


@pytest.fixture
def booking(user, centre, test):
    return Booking.objects.create(
        user=user,
        centre=centre,
        test=test,
        appointment_datetime=(
            timezone.now()
            + timedelta(days=2)
        ),
        amount=test.price,
        status=BookingStatus.PENDING,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_successful_payment(
    client,
    user,
    booking,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/payments/",
        {
            "booking_id": booking.id,
            "simulated_status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 201

    booking.refresh_from_db()

    assert (
        booking.status
        == BookingStatus.CONFIRMED
    )

    payment = Payment.objects.get(
        booking=booking
    )

    assert (
        payment.status
        == PaymentStatus.SUCCESS
    )


@pytest.mark.django_db
def test_failed_payment(
    client,
    user,
    booking,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/payments/",
        {
            "booking_id": booking.id,
            "simulated_status": "FAILED",
        },
        format="json",
    )

    assert response.status_code == 201

    booking.refresh_from_db()

    assert (
        booking.status
        == BookingStatus.FAILED
    )


@pytest.mark.django_db
def test_webhook_is_idempotent(
    client,
    user,
    booking,
):
    client.force_authenticate(user=user)

    payment_response = client.post(
        "/api/payments/",
        {
            "booking_id": booking.id,
            "simulated_status": "SUCCESS",
        },
        format="json",
    )

    payment = Payment.objects.get(
        booking=booking
    )

    # Reset to pending to demonstrate webhook transition.
    payment.status = PaymentStatus.PENDING
    payment.save()

    booking.status = BookingStatus.PENDING
    booking.save()

    event_id = "evt_test_001"

    payload = {
        "event_id": event_id,
        "event_type": "payment.updated",
        "payment_id": str(
            payment.provider_payment_id
        ),
        "status": "SUCCESS",
    }

    first_response = client.post(
        "/api/payments/webhook/",
        payload,
        format="json",
    )

    second_response = client.post(
        "/api/payments/webhook/",
        payload,
        format="json",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        PaymentWebhookEvent.objects.filter(
            event_id=event_id
        ).count()
        == 1
    )

    payment.refresh_from_db()
    booking.refresh_from_db()

    assert (
        payment.status
        == PaymentStatus.SUCCESS
    )

    assert (
        booking.status
        == BookingStatus.CONFIRMED
    )


@pytest.mark.django_db
def test_payment_for_invalid_booking(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/payments/",
        {
            "booking_id": 999999,
            "simulated_status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_cannot_be_processed_twice(
    client,
    user,
    booking,
):
    client.force_authenticate(user=user)

    first_response = client.post(
        "/api/payments/",
        {
            "booking_id": booking.id,
            "simulated_status": "SUCCESS",
        },
        format="json",
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/payments/",
        {
            "booking_id": booking.id,
            "simulated_status": "SUCCESS",
        },
        format="json",
    )

    assert second_response.status_code == 400

    assert Payment.objects.filter(
        booking=booking
    ).count() == 1