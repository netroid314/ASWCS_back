from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.http import HttpResponse

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from credit.forms import OrderForm
from credit.models import Order, OrderPayment

User=get_user_model()

def get_credit_log(request):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = request.META.get("HTTP_AUTH")['key']
    user=User.objects.get(key=key)

    if user==None:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    
    logs=list(CreditLog.objects.filter(user=user))

    return JsonResponse({
            "is_successful":True,
            "logs":logs,
            "message":"Successfully got credit log"
    })

def home(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            payment = OrderPayment.from_order(order)

            return HttpResponseRedirect(reverse('payment:pay', args=[payment.pk]))
    else:
        form = OrderForm(initial={
            'name': '크레딧 충전',
            'amount': 1000,
            'buyer': '홍길동',
            'addr': '주소',
            'subaddr': '상세주소',
            'postcode': '123-456',
            'email': 'iamport@siot.do',
            'tel': '010-1234-5678'
        })

    return render(request, 'home.html', {'form': form})


def retry_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    payment = OrderPayment.from_order(order)

    return HttpResponseRedirect(reverse('payment:pay', args=[payment.pk]))
