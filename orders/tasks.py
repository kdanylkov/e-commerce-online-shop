from celery import shared_task
from django.core.mail import send_mail
from environs import Env

from .models import Order

env = Env()
env.read_env()


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
                          env.str('SENDER'),
                          [order.email])

    return mail_sent
