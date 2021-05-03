from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from ast import literal_eval

from tempfile import TemporaryFile

import json
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from manage import schedule_manager

User=get_user_model()
INVALID = -1

def create_project(request):
    if request.method!='POST':
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
    rrs = request.POST.get('rrs', 'dummy')
    model_url = request.POST.get('model_url', 'dummy')
    max_contributor = request.POST.get('max_contributor', 5)
    status = 'STANDBY'
    created_at = timezone.now()
    started_at = timezone.now()
    finished_at = timezone.now()

    project=Project.objects.create(uid=uid,owner=user,rrs_url=rrs,model_url=model_url,
        max_contributor=max_contributor,status=status,created_at=created_at,
        started_at=started_at, finished_at=finished_at)


    numpy_file = request.FILES.get('weight', INVALID)

    if(numpy_file == INVALID):
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Numpy data"
        })

    init_weight = np.load(request.FILES.get('weight'),allow_pickle = True)

    schedule_manager.init_project(project_id=uid,total_step=3,step_size=1,weight=init_weight)

    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
        "rrs_url":rrs,
        "model_url":model_url,
        "message":"Project successfully created."
    })

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

def upload_data(requset):
    return None

def get_project_result(request, project_uid):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    if schedule_manager.is_project_finished(project_id = project_uid):
        with TemporaryFile() as tf:
            np.save(tf, schedule_manager.get_project_result(project_id=project_uid))
            _ = tf.seek(0)
            return HttpResponse(tf,content_type='application/file')

    return JsonResponse({
            "is_successful":False,
            "project_uid":project_id,
            "message":"Project Not Finished"
        })

    return None

def pause_project(request, project_uid):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

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

def get_available_project(request):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    project_id = _get_valid_project()

    if(project_id != task_number):
        return JsonResponse({
            "is_successful": True,
            "project_uid": project_id,
            "message":"Possible Project Found"
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"No Possible Project"
        })

def get_task_index(request, project_uid):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    task_index = _get_valid_task(project_uid)

    if(task_index > INVALID):
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_uid,
            "task_index":task_index,
            "message":"Available task found"
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "project_uid":project_uid,
            "message":"No available task"
        })

    return None


def start_project_task(request, project_uid):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    task_index = request.POST.get('task_index', INVALID)
    if(task_index.isdecimal()):
        task_index = int(task_index)
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid index"
        })

    if(task_index != INVALID):
        _start_task(project_id=project_uid, task_id=task_index)
        return JsonResponse({
            "is_successful":True,
            "message":"Proejct task occupied"
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid task item value"
        })


def update_project_task(request, project_uid):
    if request.method!='POST':
        return HttpResponse(json.dumps({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        }),content_type='application/json')

    key = literal_eval(request.META.get('HTTP_AUTH'))['key']
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result
    
    task_index = request.POST.get('task_index', INVALID)
    numpy_file = request.FILES.get('gradient', INVALID)

    if(numpy_file == INVALID):
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Numpy data"
        })

    gradient = np.load(request.FILES.get('gradient'),allow_pickle = True)

    if(task_index.isdecimal()):
        task_index = int(task_index)
    else:
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid index"
        })

    if((task_index == INVALID)):
        return JsonResponse({
            "is_successful":False,
            "message":"INVALID items found"
        })
    else:
        result = _update_project(project_id=project_uid,task_id=task_index,gradient=gradient)
        if(result == INVALID):
            return JsonResponse({
            "is_successful":False,
            "message":"Unavailable Index"
            })

        return JsonResponse({
            "is_successful":True,
            "message":"Gradient Updated"
        })



# Belows are not for http requests. Belows are blocks for them

def check_authorization(authorization_key):
    if User.objects.filter(key=authorization_key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    else:
        return False

def _get_valid_project(project_id):
    return schedule_manager.get_valid_project()

def _get_valid_task(project_id):
    return schedule_manager.get_valid_task(project_id=project_id)

def _start_task(project_id, task_id):
    schedule_manager.start_project_task(project_id=project_id, task_no=task_id)

def _update_project(project_id, task_id, gradient):
    return schedule_manager.update_project(project_id=project_id, task_no=task_id, gradient=gradient)