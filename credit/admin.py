from django.contrib import admin
from .models import *


class CreditLogAdmin(admin.ModelAdmin):
    model=CreditLog

    list_display=(
        'user',
        'action',
        'amount',
        'date'
    )


admin.site.register(CreditLog,CreditLogAdmin)

# Register your models here.
