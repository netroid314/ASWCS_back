from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('log',get_credit_log),
    
]