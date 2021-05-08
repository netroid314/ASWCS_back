from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
import boto3
import json

from tempfile import TemporaryFile

import json
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from manage import schedule_manager

User = get_user_model()
INVALID = -1

def create_project(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = request.META.get('HTTP_AUTH')
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
    epoch = request.POST.get('epoch', 5)
    total_task = request.POST.get('total_task', '15')
    step_size = request.POST.get('step_size', '5')

    total_task = int(total_task)
    step_size = int(step_size)

    status = 'STANDBY'
    created_at = timezone.now()

    project = Project.objects.create(uid=uid,owner=user,model_url=model_url,
        max_contributor=max_contributor,status=status,created_at=created_at)


    numpy_file = request.FILES.get('weight', INVALID)

    if(numpy_file == INVALID):
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Numpy data"
        })

    init_weight = np.load(request.FILES.get('weight'),allow_pickle = True)

    schedule_manager.init_project(project_id=uid,total_step=total_task,step_size=step_size,weight=init_weight)

    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
        "model_url":model_url,
        "total_task":total_task,
        "step_size":step_size,
        "message":"Project successfully created."
    })

def start_project(request, project_uid): 
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = request.META.get('HTTP_AUTH')
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    
    target_project = Project.objects.filter(uid = project_uid)

    if(target_project.exists()):
        target_project.update(status='INPROGRESS')
        schedule_manager.start_project(project_uid)
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_uid,
            "message":"Project successfully launched."
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "project_uid":project_uid,
            "message":"Project does not exists"
        })

    return None

def upload_data(requset):
    return None

# 아래와 같은 형태로 data 받음
# {
#     "project_uid":"",
#     "train_data":[{
#         "filename":"",
#         "file_path":"" 
#      }]
# }
# def get_upload_url(request, project_uid):
#     service_name = 's3'
#     endpoint_url = 'https://kr.object.ncloudstorage.com'
#     region_name = 'kr-standard'
#     access_key = '0C863406F8D54433789F'
#     secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

#     s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
#                       aws_secret_access_key=secret_key)

#     # project_uid=request.POST.get('project_uid')
#     train_data=json.loads(request.body)["train_data"]
#     print(train_data)

#     bucket_name='daig'
    
#     project=Project.objects.get(uid=project_uid)
#     res_data=[]
#     for td in train_data:
#         task=Task.objects.create(project=project)
#         object_name=f'project/{project_uid}/task/{task.uid}/{td["filename"]}'
#         url=s3.generate_presigned_url("put_object",Params={
#             'Bucket':bucket_name,
#             'Key':object_name
#         }, ExpiresIn=3600)
#         task.save()
#         res_data.append({
#             "file_path":td["file_path"],
#             "url":url
#         })

#     return JsonResponse({
#         "data":res_data
#     })
# -----------------------------------------------------------------------------

# 아래와 같은 형태로 data 받음
# {
#     "project_uid":"",
#     "filename":"",
# }
def generate_task_url(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key=eval(request.META.get('HTTP_AUTH')).get("key")
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    request_data=json.loads(request.body)
    bucket_name='daig'

    project=Project.objects.get(uid=project_uid)

    task=Task.objects.create(project=project)
    task.rrs_url=f'project/{project_uid}/task/{task.uid}/{request_data["filename"]}'
    task.save()

    url=s3.generate_presigned_url("put_object",Params={
        'Bucket':bucket_name,
        'Key':task.rrs_url
    }, ExpiresIn=3600)
    
    res_data={
        "is_succesful":True,
        "url":url
    }

    return JsonResponse(res_data)

# 아래와 같은 형태로 data 받음
# {
#     "project_uid":"",
#     "filename":"",
# }
def generate_model_url(request):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key=eval(request.META.get('HTTP_AUTH')).get("key")
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    request_data=json.loads(request.body)
    bucket_name='daig'

    project=Project.objects.get(uid=project_uid)
    project.model_url=f'project/{project_uid}/model/{request_data["filename"]}'
    project.save()

    url=s3.generate_presigned_url("put_object",Params={
        'Bucket':bucket_name,
        'Key':project.model_url
    }, ExpiresIn=3600)
    
    res_data={
        "is_succesful":True,
        "url":url
    }

    return JsonResponse(res_data)

def get_project_weight(request, project_uid):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    with TemporaryFile() as tf:
        np.save(tf, schedule_manager.get_project_weight(project_id=project_uid))
        _ = tf.seek(0)
        return HttpResponse(tf,content_type='application/file')

    return JsonResponse({
            "is_successful":False,
            "project_uid":project_id,
            "message":"Internal Error"
        })


def get_project_result(request, project_uid):
    if request.method!='GET':
        return HttpResponse(status = '270')

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    if schedule_manager.is_project_finished(project_id = project_uid):
        with TemporaryFile() as tf:
            np.save(tf, schedule_manager.get_project_result(project_id=project_uid))
            _ = tf.seek(0)
            return HttpResponse(tf,content_type='application/file')

    return HttpResponse(status = '270')

def pause_project(request, project_uid):
    if request.method!='POST':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] POST ONLY"
        })

    key = request.META.get('HTTP_AUTH')
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

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    project_id = _get_valid_project()

    if(project_id != -1):
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

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    task_index = _get_valid_task(project_id=project_uid)
    total_task_number = _get_total_task_number(project_id=project_uid)

    if(task_index > INVALID):
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_uid,
            "task_index":task_index,
            "total_task":total_task_number,
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

    key = request.META.get('HTTP_AUTH')
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

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result
    
    task_index = request.POST.get('task_index', INVALID)
    spent_time = request.POST.get('spent_time', 5)
    numpy_file = request.FILES.get('gradient', INVALID)

    if ((task_index == INVALID) or (spent_time == INVALID) or (numpy_file == INVALID)):
        return JsonResponse({
            "is_successful":False,
            "message":"INVALID params detected"
        })

    gradient = np.load(numpy_file,allow_pickle = True)

    result = _update_project(project_id=project_uid,task_id=task_index,gradient=gradient, time = spent_time)
    if(result == INVALID):
        return JsonResponse({
        "is_successful":False,
        "message":"Gradient Update fail. expired index"
        })

    return JsonResponse({
        "is_successful":True,
        "message":"Gradient Updated Success"
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

def _get_valid_project():
    return schedule_manager.get_valid_project()

def _get_valid_task(project_id):
    return schedule_manager.get_valid_task(project_id=project_id)

def _get_total_task_number(project_id):
    return schedule_manager.get_total_task_number(project_id=project_id)

def _start_task(project_id, task_id):
    schedule_manager.start_project_task(project_id=project_id, task_no=task_id)

def _update_project(project_id, task_id, gradient, time):
    return schedule_manager.update_project(project_id=project_id, task_no=task_id, gradient=gradient, time = time)
    
def _load_projects_from_DB():
    return 1
    # gonna do this far later

def get_upload_url(request, project_uid):
    key=eval(request.META.get('HTTP_AUTH')).get("key")
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    user=User.objects.get(key=key)

    projects=Project.objects.filter(status="in_progress").all()

    project=projects[0] # project 선택 방법 추가/수정 필요


    tasks=Task.objects.filter(project=p, status="not_started").all()

    task=tasks[0] # task 선택 방법 추가/수정 필요


    task.tasker=user
    task.status="assgined"
    task.save()

    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name='daig'
    url=s3.generate_presigned_url("get_object",Params={
        'Bucket':bucket_name,
        'Key':task.rrs_url
    }, ExpiresIn=3600)

    res_data={
        "project_uid":project.uid,
        "task_uid":task.uid,
        "url":url
    }
    
    return res_data
