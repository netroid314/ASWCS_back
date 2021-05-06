from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from .views import *

urlpatterns = [
    path('log',get_credit_log),
    url('charge', charge_credit),
    url('checkout', CreditCheckoutView, name ='credit_checkout'),
    url('validation', CreditImpView, name = 'credit_validation'),
    url('admin/', admin.site.urls),
]