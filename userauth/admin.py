from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import *

user=get_user_model()
class UserAdmin_2(UserAdmin):
    model=user

    list_display = (
        'username',
        'user_SN',
        'date_joined'
    )

    list_display_links = (
        'username',
    )

    fieldsets=[
        (None, {'fields': ('username', 'password', 'date_joined')})
    ]

class CreditLogAdmin(admin.ModelAdmin):
    model=CreditLog

    list_display=(
        'user',
        'action',
        'amount',
        'date'
    )



# admin.site.register(User)

admin.site.register(user,UserAdmin_2)
admin.site.register(CreditLog,CreditLogAdmin)
# Register your models here.
