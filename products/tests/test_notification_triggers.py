import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from products.models import Product
from orders.services.order_service import OrderService

User = get_user_model()


@pytest.mark.django_db
def test_order_creation_triggers_email_and_sms():
    user = User.objects.create_user(
        "notify", "n@test.com", "pass"
    )

    product = Product.objects.create(
        name="Sofa",
        price=5000,
        stock=5,
        is_active=True,
    )

    with patch("notifications.tasks.send_email_task.delay") as email_mock, \
         patch("notifications.tasks.send_sms_task.delay") as sms_mock:

        OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}],
        )

        email_mock.assert_called_once()
        sms_mock.assert_called_once()
