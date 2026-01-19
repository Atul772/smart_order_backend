import pytest
from django.contrib.auth import get_user_model
from products.models import Product
from orders.services.order_service import OrderService

User = get_user_model()


@pytest.mark.django_db
def test_transaction_rollback_on_partial_failure():
    user = User.objects.create_user("t1", "t@test.com", "pass")
    product = Product.objects.create(
        name="Shelf", price=1000, stock=2, is_active=True
    )

    with pytest.raises(Exception):
        OrderService.create_order(
            user=user,
            items=[
                {"product_id": product.id, "quantity": 1},
                {"product_id": 9999, "quantity": 1},
            ]
        )

    product.refresh_from_db()
    assert product.stock == 2
