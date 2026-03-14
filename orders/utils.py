from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)

    subject = f"Order confirmation #{order.id}"
    message = f"""
    Thank you for your order!

    Your order ID is {order.id}.
    We will notify you once your order is shipped.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
    )