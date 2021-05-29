from django.forms import ModelForm

from credit.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ['pay_status','tel']
