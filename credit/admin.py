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


class PaymentInline(admin.StackedInline):
    model = OrderPayment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [PaymentInline]


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    pass

# Register your models here.
