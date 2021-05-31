from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from .views import *
from . import views

app_name = "credit"

urlpatterns = [
    path('remains/',get_current_credit),
    path('log/',get_credit_log),
    url('admin/', admin.site.urls),
    path('payment/', views.home, name='home'),
    path('retry_order/<int:order_id>', views.retry_order, name='retry_order'),
]