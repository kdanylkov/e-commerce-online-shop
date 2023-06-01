from decimal import Decimal
import stripe

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.http import HttpRequest

from orders.models import Order
from cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request: HttpRequest):
    order_id = request.session.get('order_id', None)
    order: Order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
                'mode': 'payment',
                'client_reference_id': order.id,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'line_items': []
                }

        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name
                        },
                     },
                'quantity': item.quantity,
                })

        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                    name=order.coupon.code,
                    percent_off=order.discount,
                    duration='once'
                    )
            session_data['discounts'] = [{
                'coupon': stripe_coupon.id
                }]
        session = stripe.checkout.Session.create(**session_data)

        remove_coupon_from_cart_and_session(request)
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', {'order': order})


def payment_completed(request: HttpRequest):
    return render(request, 'payment/completed.html')


def payment_canceled(request: HttpRequest):
    return render(request, 'payment/canceled.html')


def remove_coupon_from_cart_and_session(request: HttpRequest):
    del request.session['coupon_id']
    request.session.modified = True

    cart = Cart(request)
    cart.coupon_id = None
