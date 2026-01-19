import pytest
from django.contrib.auth import get_user_model
from products.models import Product
from orders.services.order_service import OrderService
from payments.services.payment_service import PaymentService
from payments.models import Payment

User = get_user_model()


@pytest.mark.django_db
class TestPaymentService:

    def test_initiate_payment_success(self):
        user = User.objects.create_user("p1", "p1@test.com", "pass")
        product = Product.objects.create(
            name="Desk", price=2000, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}]
        )

        payment = PaymentService.initiate_payment(user, order.id)

        assert payment.status == payment.Status.INITIATED

    def test_initiate_payment_twice_not_allowed(self):
        user = User.objects.create_user("p2", "p2@test.com", "pass")
        product = Product.objects.create(
            name="Mirror", price=500, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}]
        )

        payment1 = PaymentService.initiate_payment(user, order.id)
        payment2 = PaymentService.initiate_payment(user, order.id)

        assert payment1.id == payment2.id
        assert payment2.status == Payment.Status.INITIATED


    def test_complete_payment_success(self):
        user = User.objects.create_user("p3", "p3@test.com", "pass")
        product = Product.objects.create(
            name="Bed", price=10000, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}]
        )

        payment = PaymentService.initiate_payment(user, order.id)
        PaymentService.complete_payment(payment.id, "SUCCESS", "TXN123")

        order.refresh_from_db()
        assert order.status == order.Status.PAID

    def test_duplicate_payment_success_callback(self):
        user = User.objects.create_user("p4", "p4@test.com", "pass")
        product = Product.objects.create(
            name="Wardrobe", price=15000, stock=5, is_active=True
        )

        order = OrderService.create_order(
            user=user,
            items=[{"product_id": product.id, "quantity": 1}]
        )

        payment = PaymentService.initiate_payment(user, order.id)
        PaymentService.complete_payment(payment.id, "SUCCESS", "TXN123")

        with pytest.raises(Exception):
            PaymentService.complete_payment(payment.id, "SUCCESS", "TXN123")
