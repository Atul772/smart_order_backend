import pytest
from django.contrib.auth import get_user_model
from products.models import Product
from orders.services.order_service import OrderService
from payments.services.payment_service import PaymentService

User = get_user_model()


@pytest.mark.django_db
class TestOrderService:

    def test_create_order_success(self):
        user = User.objects.create_user("u1", "u1@test.com", "pass")
        product = Product.objects.create(
            name="Chair", price=1000, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 2}]
        )

        product.refresh_from_db()

        assert order.total_amount == 2000
        assert product.stock == 3
        assert order.status == order.Status.CREATED

    def test_create_order_insufficient_stock(self):
        user = User.objects.create_user("u2", "u2@test.com", "pass")
        product = Product.objects.create(
            name="Table", price=500, stock=1, is_active=True
        )

        with pytest.raises(Exception):
            OrderService.create_order(
                user=user,
                items=[{"product_id": product.id, "quantity": 2}]
            )

        product.refresh_from_db()
        assert product.stock == 1

    def test_create_order_inactive_product(self):
        user = User.objects.create_user("u3", "u3@test.com", "pass")
        product = Product.objects.create(
            name="Sofa", price=1000, stock=5, is_active=False
        )

        with pytest.raises(Exception):
            OrderService.create_order(
                user=user,
                items=[{"product_id": product.id, "quantity": 1}]
            )

    def test_cancel_order_success(self):
        user = User.objects.create_user("u4", "u4@test.com", "pass")
        product = Product.objects.create(
            name="Lamp", price=300, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 2}]
        )

        OrderService.cancel_order(user=user, order_id=order.id)

        order.refresh_from_db()
        product.refresh_from_db()

        assert order.status == order.Status.CANCELLED
        assert product.stock == 5

    def test_cancel_paid_order_not_allowed(self):
        user = User.objects.create_user("u5", "u5@test.com", "pass")
        product = Product.objects.create(
            name="Fan", price=800, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}]
        )

        payment = PaymentService.initiate_payment(user, order.id)
        PaymentService.complete_payment(payment.id, "SUCCESS")

        with pytest.raises(Exception):
            OrderService.cancel_order(user=user, order_id=order.id)
