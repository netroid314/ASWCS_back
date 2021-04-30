from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from .views import *

urlpatterns = [
    path('log',get_credit_log),
    url('charge', charge_credit),
    url('checkout', CreditCheckoutView),
    url('validation', CreditImpView),
    url('admin/', admin.site.urls),
]