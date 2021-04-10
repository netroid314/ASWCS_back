from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User

def login(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"POST ONLY"
        })

    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    myuser = User.objects.get(username=username) 
    if myuser.check_password(password):
        return JsonResponse({
            "is_successful":True,
            "message":"Login Successful",
            "auth":{
                "key":myuser.key
            }
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Wrong Password"
        })



# Create your views here.
