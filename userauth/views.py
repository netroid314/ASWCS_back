from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from .models import User
from bson.objectid import ObjectId
from uuid import uuid4
import random
import string
import threading

email_code={}
timer={}

def login(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    if User.objects.filter(username=username).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Non-existed username"
        })

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

def sign_up(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })
    
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    email = request.POST.get('email', None)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            "is_successful":False,
            "message":"Already existed username."
        })
    
    user=User.objects.create(username=username,user_SN=str(ObjectId()),key=str(uuid4()), email=email)
    user.set_password(password)
    user.save()


    return JsonResponse({
        "is_successful":True,
        "message":"Successfully signed up."
    })

def del_code(email):
    saved_code=email_code.get(email)
    if saved_code!=None:
        del email_code[email]
    

def send_email(request):
    email=request.POST.get('email',None)
    if email==None:
        return JsonResponse({
            "is_successful":False,
            "message":"No email detected."
        })
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            "is_successful":False,
            "message":"Already existed email."
        })

    code = ''
    for r in range(7):
        code += random.choice(string.ascii_letters)
    
    message_title = 'DAIG Service Verification Email'
    message_context = f'Verification code: \n\n{code}'

    message=EmailMessage(
        message_title,
        message_context,
        to=[email]
    )

    if message.send():
        if timer.get(email)!=None:
            timer[email].cancel()
            del timer[email]
        email_code[email]=code
        timer[email]=threading.Timer(600,del_code,(email,))
        timer[email].start()
        return JsonResponse({
            "is_successful":True,
            "message":"Sent Email"
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Sending Email Error"
        })

def verify_code(request):
    email=request.POST.get('email',None)
    code=request.POST.get('code',None)
    if email==None or code==None:
        return JsonResponse({
            "is_successful":False,
            "message":"Input Error"
        })

    saved_code=email_code.get(email)
    if saved_code==None:
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Email"
        })

    if saved_code==code:
        del email_code[email]
        timer[email].cancel()
        del timer[email]
        return JsonResponse({
            "is_successful":True,
            "message":"Successfully verified email"
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Check verification code"
        })


def check_username(request):
    username=request.POST.get('username',None)
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            "is_successful":False,
            "message":"Already existed ID"
        })
    else:
        return JsonResponse({
            "is_successful":True,
            "message":"Available ID"
        })

# Create your views here.
