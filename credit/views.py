from django.shortcuts import render
from django.http import JsonResponse
from .models import *


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

class CreditCheckoutView():
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return JsonResponse({}, status=401)

        user = request.user
        amount = request.POST.get('amount')
        type = request.POST.get('type')

        try:
            pay = CreditPayment.objects.create_new(
                user=user,
                amount=amount,
                type=type
            )
        except:
            pay = None

        if pay is not None:
            data = {
                "works": True,
                "merchant_id": pay
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


class CreditImpView():
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return JsonResponse({}, status=401)

        user = request.user
        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            pay = CreditPayment.objects.get(
                user=user,
                order_id=merchant_id,
                amount=amount
            )
        except:
            pay = None

        if pay is not None:
            pay.transaction_id = imp_id
            pay.success = True
            pay.save()

            data = {
                "works": True
            }

            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)

def charge_credit(request):
    template = 'charge.html'

    return render(request, template)
