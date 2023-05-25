from decimal import Decimal
from django.conf import settings
from django.http import HttpRequest

from shop.models import Product


class Cart:

    def __init__(self, request: HttpRequest):
        """
        Initialize the cart
        """

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1,
            override_quantity: bool = False) -> None:
        """
        Adding a product to the cart or updating it's quantity
        """
        product_id = str(product.id)
        if product.id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Method to make sure the session gets saved by setting its
        `modified` paramenter to True
        """
        self.session.modified = True

    def remove(self, product: Product):
        """
        Method to remove the given product from the cart
        """
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Method to iterate over the items in the cart and pull the
        corresponding products from the database.
        """
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Method to count the amount of items in the cart
        """
        return sum(item['quanity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Method that returns the total price of all items stored in the cart.
        """
        return sum(Decimal(item['price'] * item['quantity']
                           for item in self.cart.values()))

    def clear(self):
        """
        Method that allows to remove all items from the cart
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()