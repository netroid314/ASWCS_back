from django.shortcuts import render
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


# Create your views here.
