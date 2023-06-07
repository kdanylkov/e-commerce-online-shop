from django import forms
from localflavor.ru.forms import RUPostalCodeField
from localflavor.us.forms import USZipCodeField

from .models import Order


class OrderCreationFormRu(forms.ModelForm):
    postal_code = RUPostalCodeField()

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
                  'postal_code', 'city']


class OrderCreationFormUs(forms.ModelForm):
    postal_code = USZipCodeField()

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
                  'postal_code', 'city']


class OrderCreationForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
                  'postal_code', 'city']
