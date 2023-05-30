from django.forms import Form, CharField


class CouponApplyForm(Form):
    code = CharField()
