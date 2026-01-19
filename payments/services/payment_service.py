from django.db import transaction
from django.core.exceptions import PermissionDenied
from orders.models import Order
from payments.models import Payment
from notifications.tasks import send_email_task
from notifications.tasks import send_sms_task
import logging
from config.middleware import get_request_id

request_id = get_request_id()

logger = logging.getLogger(__name__)


class PaymentService:

    @staticmethod
    @transaction.atomic
    def initiate_payment(user, order_id):
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order does not exist")

        # Authorization
        if order.user != user and not user.is_admin:
            raise PermissionDenied("You are not allowed to pay for this order")

        # Order state check
        if order.status != Order.Status.CREATED:
            raise ValueError("Payment cannot be initiated for this order")

        # Prevent duplicate payment
        if hasattr(order, "payment"):
            payment = order.payment

            if payment.status == Payment.Status.SUCCESS:
                raise ValueError("Payment already completed")

            if payment.status == Payment.Status.INITIATED:
                return payment  # idempotent retry

            if payment.status == Payment.Status.FAILED:
                payment.status = Payment.Status.INITIATED
                payment.transaction_id = None
                payment.save()
                return payment

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            status=Payment.Status.INITIATED,
        )

        return payment

    @staticmethod
    @transaction.atomic
    def complete_payment(payment_id, status, transaction_id=None):
        logger.info(f"Payment completion requested: payment_id={payment_id}, status={status}")

        try:
            payment = Payment.objects.select_for_update().get(id=payment_id)

            if payment.status == Payment.Status.FAILED and status == "FAILED":
                logger.info(f"Idempotent FAILED payment ignored: payment_id={payment_id}")
                return payment

        except Payment.DoesNotExist:
            logger.error(f"Payment not found: payment_id={payment_id}")
            raise ValueError("Payment does not exist")

        order = payment.order

        if order.status == Order.Status.CANCELLED:
            logger.warning(
                f"Payment attempt on cancelled order: order_id={order.id}, payment_id={payment_id}"
            )
            raise ValueError("Cannot complete payment for cancelled order")

        if payment.status == Payment.Status.SUCCESS:
            logger.warning(f"Duplicate SUCCESS callback ignored: payment_id={payment_id}")
            raise ValueError("Payment already completed")

        if status == "SUCCESS":
            logger.info(f"Processing SUCCESS payment: payment_id={payment_id}")

            payment.status = Payment.Status.SUCCESS
            payment.transaction_id = transaction_id
            order.status = Order.Status.PAID

            request_id = get_request_id()

            send_email_task.delay(
                subject="Payment Successful",
                message=f"Payment successful for Order #{order.id}.",
                recipient_list=[order.user.email],
                request_id=request_id,
            )

            send_sms_task.delay(
                phone_number="+917808040719",
                message=f"Payment successful for Order #{order.id}.",
                request_id=request_id,
            )

            logger.info(
                f"Payment SUCCESS completed: payment_id={payment.id}, order_id={order.id}"
            )

        elif status == "FAILED":
            logger.info(f"Processing FAILED payment: payment_id={payment_id}")

            payment.status = Payment.Status.FAILED
            order.status = Order.Status.CREATED  # retry allowed

        payment.save()
        order.save()

        logger.info(
            f"Payment state persisted: payment_id={payment.id}, "
            f"payment_status={payment.status}, order_status={order.status}"
        )

        return payment
