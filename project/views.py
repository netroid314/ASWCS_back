from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from ast import literal_eval

import numpy as np
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

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    user=User.objects.get(key=key)

    uid = str(ObjectId())
    rrs = request.GET.get('rrs', 'dummy')
    model_url = request.GET.get('model_url', 'dummy')
    max_contributor = request.GET.get('max_contributor', 5)
    status = 'STANDBY'
    created_at = timezone.now()
    started_at = timezone.now()
    finished_at = timezone.now()

    project=Project.objects.create(uid=uid,owner=user,rrs_url=rrs,model_url=model_url,
        max_contributor=max_contributor,status=status,created_at=created_at,
        started_at=started_at, finished_at=finished_at)

    # Erase this test code later
    tmp_init_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
    tmp_init_weight = np.array(tmp_init_weight, dtype=object) 

    schedule_manager.init_project(project_id=uid,total_step=30,step_size=5,weight=tmp_init_weight)

    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
        "rrs_url":rrs,
        "model_url":model_url,
        "message":"Project successfully created."
    })

def upload_data(request, project_uid):

    return None

def start_project(request, project_uid): 
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    
    project_id = request.POST.get('project_id', None)
    target_project =  Project.objects.filter(uid = project_id)

    if(target_project.exists()):
        target_project.update(status='INPROGRESS')
        schedule_manager.start_project(project_id)
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_id,
            "message":"Project successfully launched."
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "project_uid":project_id,
            "message":"Project does not exists"
        })

    return None

def get_project_result(request, project_uid): 
    return None

def pause_project(request, project_uid):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    
    project_id = request.POST.get('project_id', None)
    target_project =  Project.objects.filter(uid = project_id)

    if(target_project.exists()):
        target_project.update(status='STANDBY')
        schedule_manager.pause_project(project_id)
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_id,
            "message":"Project successfully paused."
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "project_uid":project_id,
            "message":"Project does not exists"
        })

    return None

def get_project_progress(request, project_uid):
    return None
