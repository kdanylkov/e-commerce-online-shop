from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from .forms import OrderCreationForm
from .services import create_order_in_db
from cart.cart import Cart
from .tasks import mail_order_created


def order_create(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreationForm(request.POST)
        order = create_order_in_db(form, cart)
        if order:
            mail_order_created.delay(order.id)

            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreationForm()
    return render(request,
                  'orders/order/create.html',
                  {'form': form, 'cart': cart})
