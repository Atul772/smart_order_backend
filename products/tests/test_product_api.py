import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from products.models import Product


@pytest.mark.django_db
def test_product_list_shows_only_available_products():
    client = APIClient()

    Product.objects.create(
        name="Available Product",
        price=1000,
        stock=5,
        is_active=True,
    )

    Product.objects.create(
        name="Inactive Product",
        price=1000,
        stock=5,
        is_active=False,
    )

    Product.objects.create(
        name="Out of Stock Product",
        price=1000,
        stock=0,
        is_active=True,
    )

    response = client.get(reverse("product-list"))

    names = [p["name"] for p in response.data]

    assert "Available Product" in names
    assert "Inactive Product" not in names
    assert "Out of Stock Product" not in names
