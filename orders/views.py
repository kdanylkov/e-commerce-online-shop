from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse

from .forms import OrderCreationForm
from .services import create_order_in_db
from cart.cart import Cart
from .tasks import mail_order_created
from .models import Order


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


@staff_member_required
def admin_order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})
