from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

import weasyprint

from .forms import OrderCreationFormRu, OrderCreationFormUs, OrderCreationForm
from .services import create_order_in_db
from cart.cart import Cart
from .tasks import mail_order_created, update_recommendations
from .models import Order


def order_create(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if request.method == 'POST':
        language = request.LANGUAGE_CODE
        if language in ('ru', 'ru-ru'):
            form = OrderCreationFormRu(request.POST)
        elif language in ('en-us', 'en'):
            form = OrderCreationFormUs(request.POST)
        else:
            form = OrderCreationForm(request.POST)

        order = create_order_in_db(form, cart)
        if order:
            mail_order_created.delay(order.id)
            update_recommendations.delay(order.id)

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


@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order, id=order_id)

    html = render_to_string('orders/order/pdf.html', {'order': order})

    response = HttpResponse(
        content_type='application/pdf',
        headers={
            'Content-Disposition': f'filename=order_{order.id}.pdf'
        })
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')])

    return response
