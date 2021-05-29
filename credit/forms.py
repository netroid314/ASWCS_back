from django.forms import ModelForm, widgets
from django import forms
from credit.models import Order
'''
CREDIT_CHOICES ={
('1000원',1000),
('2000원',2000),
('5000원',5000),
('10000원',10000),
('30000원',30000),
('50000원',50000)

}
'''
class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['userKey','amount','email','buyer','name']
        widgets = {
            'userKey' : forms.HiddenInput(),
            'name' : forms.HiddenInput()
        }

