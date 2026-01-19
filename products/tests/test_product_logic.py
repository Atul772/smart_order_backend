import pytest
from products.models import Product
from django.core.cache import cache


@pytest.mark.django_db
class TestProductLogic:

    def test_active_product_with_stock_is_available(self):
        product = Product.objects.create(
            name="Mattress",
            price=10000,
            stock=5,
            is_active=True,
        )

        assert product.is_active is True
        assert product.stock > 0

    def test_inactive_product_not_available(self):
        product = Product.objects.create(
            name="Chair",
            price=2000,
            stock=5,
            is_active=False,
        )

        assert product.is_active is False

    def test_out_of_stock_product_not_available(self):
        product = Product.objects.create(
            name="Table",
            price=3000,
            stock=0,
            is_active=True,
        )

        assert product.stock == 0
