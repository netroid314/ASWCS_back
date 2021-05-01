from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from .models import *

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from manage import schedule_manager

User=get_user_model()

def create_project(request):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = request.META.get('HTTP_AUTH')['key']
    if User.objects.filter(key==key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    user=User.objects.get(key=key)

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
