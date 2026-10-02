from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from decimal import Decimal

from diagnostics.models import (
    DiagnosticCentre,
    DiagnosticTest,
)

from .models import Booking, BookingStatus


@pytest.fixture
def user():
    return User.objects.create_user(
        username="customer",
        password="Password123",
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        username="another",
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
def client():
    return APIClient()


@pytest.mark.django_db
def test_user_can_create_booking(
    client,
    user,
    centre,
    test,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/bookings/",
        {
            "centre": centre.id,
            "test": test.id,
            "appointment_datetime": (
                timezone.now()
                + timedelta(days=2)
            ).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201

    booking = Booking.objects.get(
        user=user
    )

    assert booking.amount == Decimal(str(test.price))
    assert booking.status == BookingStatus.PENDING


@pytest.mark.django_db
def test_user_cannot_view_another_users_booking(
    client,
    user,
    another_user,
    centre,
    test,
):
    booking = Booking.objects.create(
        user=another_user,
        centre=centre,
        test=test,
        appointment_datetime=(
            timezone.now() + timedelta(days=2)
        ),
        amount=test.price,
    )

    client.force_authenticate(user=user)

    response = client.get(
        f"/api/bookings/{booking.id}/"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_past_appointment_is_rejected(
    client,
    user,
    centre,
    test,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/bookings/",
        {
            "centre": centre.id,
            "test": test.id,
            "appointment_datetime": (
                timezone.now()
                - timedelta(days=1)
            ).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_booking_can_be_cancelled(
    client,
    user,
    centre,
    test,
):
    booking = Booking.objects.create(
        user=user,
        centre=centre,
        test=test,
        appointment_datetime=(
            timezone.now() + timedelta(days=2)
        ),
        amount=test.price,
        status=BookingStatus.PENDING,
    )

    client.force_authenticate(user=user)

    response = client.post(
        f"/api/bookings/{booking.id}/cancel/"
    )

    assert response.status_code == 200

    booking.refresh_from_db()

    assert (
        booking.status
        == BookingStatus.CANCELLED
    )

@pytest.mark.django_db
def test_invalid_booking_id_returns_404(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.get(
        "/api/bookings/999999/"
    )

    assert response.status_code == 404

@pytest.mark.django_db
def test_user_cannot_modify_booking_status(
    client,
    user,
    centre,
    test,
):
    booking = Booking.objects.create(
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

    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/bookings/{booking.id}/",
        {
            "status": "CONFIRMED",
        },
        format="json",
    )

    assert response.status_code == 405


