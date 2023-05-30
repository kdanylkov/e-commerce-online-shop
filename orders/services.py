from django.db.transaction import atomic

from .models import OrderItem, Order
from .forms import OrderCreationForm
from cart.cart import Cart


@atomic
def create_order_in_db(form: OrderCreationForm, cart: Cart) -> Order:
    if form.is_valid():
        order: Order = form.save(commit=False)
        if cart.coupon:
            order.coupon = cart.coupon
            order.discount = cart.coupon.discount
        order.save()

        for item in cart:
            OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()

        return order
