from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', login),
    path('signup/', sign_up),
    path('send/email/', send_email),
    path('check/code/', verify_code)
]