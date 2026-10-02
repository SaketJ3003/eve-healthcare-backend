import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import DiagnosticCentre, DiagnosticTest


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        password="Password123",
    )


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username="staffuser",
        password="Password123",
        is_staff=True,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def centre():
    return DiagnosticCentre.objects.create(
        name="EVE Diagnostics",
        location="Jaipur",
    )


@pytest.mark.django_db
def test_authenticated_user_can_list_centres(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.get(
        "/api/diagnostics/centres/"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_non_staff_cannot_create_centre(
    client,
    user,
):
    client.force_authenticate(user=user)

    response = client.post(
        "/api/diagnostics/centres/",
        {
            "name": "Test Centre",
            "location": "Jaipur",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_can_create_centre(
    client,
    staff_user,
):
    client.force_authenticate(user=staff_user)

    response = client.post(
        "/api/diagnostics/centres/",
        {
            "name": "Test Centre",
            "location": "Jaipur",
        },
        format="json",
    )

    assert response.status_code == 201
    assert DiagnosticCentre.objects.filter(
        name="Test Centre"
    ).exists()


@pytest.mark.django_db
def test_staff_can_create_test(
    client,
    staff_user,
    centre,
):
    client.force_authenticate(user=staff_user)

    response = client.post(
        "/api/diagnostics/tests/",
        {
            "centre": centre.id,
            "name": "CBC",
            "description": "Complete Blood Count",
            "price": "500.00",
        },
        format="json",
    )

    assert response.status_code == 201
    assert DiagnosticTest.objects.filter(
        centre=centre,
        name="CBC",
    ).exists()