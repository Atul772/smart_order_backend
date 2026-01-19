from django.db import transaction
from orders.models import Order, OrderItem
from products.models import Product
from django.core.exceptions import PermissionDenied
from notifications.tasks import send_email_task
from notifications.tasks import send_sms_task
from django.core.cache import cache
import logging
from config.middleware import get_request_id

request_id = get_request_id()

logger = logging.getLogger(__name__)


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(user, items):
        """
        Create order and order items in a single transaction.
        """
        logger.info(f"Creating order for user {user.id}")

        order = Order.objects.create(user=user)
        total_amount = 0

        for item in items:
            product = Product.objects.select_for_update().get(
                id=item["product_id"]
            )

            if not product.is_active:
                raise ValueError("Product is inactive")

            if product.stock < item["quantity"]:
                raise ValueError(f"Insufficient stock for {product.name}")

            product.stock -= item["quantity"]
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                price_at_time=product.price,
            )

            total_amount += product.price * item["quantity"]

        order.total_amount = total_amount
        order.save()
        # Invalidate product list cache
        cache.delete("product_list")

        # Invalidate availability cache for ordered products
        for item in items:
            cache_key = f"product_availability_{item['product_id']}"
            cache.delete(cache_key)

        logger.info(f"Order {order.id} created successfully")

        send_email_task.delay(
            subject="Order Created",
            message=f"Your order #{order.id} has been created successfully.",
            recipient_list=[user.email],
            request_id=request_id,
        )


        send_sms_task.delay(
            phone_number="+917808040719",
            message=f"Order successful for Order #{order.id}.",
            request_id=request_id,
        )


        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(user, order_id):
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order does not exist")

        # Authorization check
        if order.user != user and not user.is_admin:
            raise PermissionDenied("You are not allowed to cancel this order")

        # State check
        if order.status != Order.Status.CREATED:
            raise ValueError("Order cannot be cancelled in current state")

        # Restore stock
        for item in order.items.select_related("product"):
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = Order.Status.CANCELLED
        order.save()

        # Invalidate product list cache
        cache.delete("product_list")

        # Invalidate availability cache for restored products
        for item in order.items.all():
            cache_key = f"product_availability_{item.product.id}"
            cache.delete(cache_key)

        return order

    @staticmethod
    def admin_update_status(admin_user, order_id, new_status):
        if not admin_user.is_admin:
            raise PermissionDenied("Only admin can update order status")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order does not exist")

        allowed_transitions = {
            Order.Status.PAID: [Order.Status.SHIPPED],
            Order.Status.SHIPPED: [Order.Status.DELIVERED],
        }

        current_status = order.status

        if current_status not in allowed_transitions:
            raise ValueError("Order status cannot be updated further")

        if new_status not in allowed_transitions[current_status]:
            raise ValueError("Invalid status transition")

        order.status = new_status
        order.save()

        return order
