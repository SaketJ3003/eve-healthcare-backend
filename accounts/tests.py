import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_signup():
    client = APIClient()

    response = client.post(
        "/api/auth/signup/",
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123",
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(
        username="testuser"
    ).exists()


@pytest.mark.django_db
def test_duplicate_email():
    User.objects.create_user(
        username="existing",
        email="test@example.com",
        password="Password123",
    )

    client = APIClient()

    response = client.post(
        "/api/auth/signup/",
        {
            "username": "newuser",
            "email": "test@example.com",
            "password": "Password123",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login():
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="Password123",
    )

    client = APIClient()

    response = client.post(
        "/api/auth/login/",
        {
            "username": "testuser",
            "password": "Password123",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_me_requires_authentication():
    client = APIClient()

    response = client.get("/api/auth/me/")

    assert response.status_code == 401