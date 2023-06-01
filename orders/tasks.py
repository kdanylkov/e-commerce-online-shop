from celery import shared_task

from django.core.mail import send_mail
from django.conf import settings

from .models import Order
from shop.recommender import Recommender


@shared_task
def mail_order_created(order_id):
    """
    Task to send e-mail notification when an order is successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order_id}'

    message = f'''
Dear {order.first_name},

You have successfully placed an order.
Your order ID is {order_id}.
    '''
    mail_sent = send_mail(subject,
                          message,
                          settings.EMAIL_SENDER,
                          [order.email])

    return mail_sent


@shared_task
def update_recommendations(order_id):
    order = Order.objects.prefetch_related('items__product').get(id=order_id)

    products = [item.product for item in order.items.all()]

    rec = Recommender()
    rec.products_bought(products)
