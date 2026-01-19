from celery import shared_task
import time
from django.core.mail import send_mail
from notifications.sms_client import send_sms
import logging


logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def test_background_task(self):
    time.sleep(3)
    print("Celery task executed successfully")
    return "done"

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def send_email_task(self, subject, message, recipient_list, request_id=None):
    logger.info(
        f"[celery][request_id={request_id}] Sending email: {subject}"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=recipient_list,
        fail_silently=False,
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def send_sms_task(self, phone_number, message, request_id=None):
    #  Circuit-breaker lite: stop after max retries
    if self.request.retries >= 3:
        logger.error(
            f"[celery][request_id={request_id}] "
            f"SMS permanently failed after retries for {phone_number}"
        )
        return

    logger.info(
        f"[celery][request_id={request_id}] Sending SMS to {phone_number}"
    )

    send_sms(phone_number, message)