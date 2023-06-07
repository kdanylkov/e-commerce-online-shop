from django.forms import Form, CharField
from django.utils.translation import gettext_lazy as _


class CouponApplyForm(Form):
    code = CharField(label=_('Coupon'))
