from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from .models import *

User=get_user_model()

def create_project(request):
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
    
    project=Project.objects.create(owner=user)
    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
        "message":"Project successfully created."
    })

def upload_data(request, project_uid):
    return None

def start_project(request, project_uid): 
    return None

def get_project_result(request, project_uid): 
    return None

def change_project_status(request, project_uid):
    return None

def get_project_progress(request, project_uid):
    return None


# Create your views here.
