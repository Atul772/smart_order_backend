import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_signup_success(self):
        url = reverse("register")  # adjust if your name differs
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123"
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == 201
        assert User.objects.filter(username="testuser").exists()

    def test_signup_duplicate_username(self):
        User.objects.create_user(
            username="testuser",
            email="t@test.com",
            password="pass"
        )

        url = reverse("register")
        payload = {
            "username": "testuser",
            "email": "new@test.com",
            "password": "StrongPass123"
        }

        response = self.client.post(url, payload, format="json")
        assert response.status_code == 400

    def test_login_success(self):
        User.objects.create_user(
            username="loginuser",
            email="login@test.com",
            password="StrongPass123"
        )

        url = reverse("token_obtain_pair")
        payload = {
            "username": "loginuser",
            "password": "StrongPass123"
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_password(self):
        User.objects.create_user(
            username="loginuser2",
            email="login2@test.com",
            password="CorrectPass"
        )

        url = reverse("token_obtain_pair")
        payload = {
            "username": "loginuser2",
            "password": "WrongPass"
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == 401
