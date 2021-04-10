from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

user=get_user_model()
class UserAdmin_2(UserAdmin):
    model=user

    list_display = (
        'username',
        'date_joined',
        'key'
    )

    list_display_links = (
        'username',
    )

    fieldsets=[
        (None, {'fields': ('username', 'password', 'date_joined')})
    ]


# admin.site.register(User)

admin.site.register(user,UserAdmin_2)
# Register your models here.
