from botocore.configprovider import SectionConfigProvider
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
import boto3
import json
import requests

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
    max_contributor = request.POST.get('max_contributor', '-1')
    epoch = request.POST.get('epoch', '5')
    batch_size = request.POST.get('batch_size', '5')
    total_task = request.POST.get('total_task', '15')
    step_size = request.POST.get('step_size', '5')
    valid_rate = request.POST.get('valid_rate','0')

    total_task = int(total_task)
    step_size = int(step_size)
    epoch = int(epoch)
    batch_size = int(batch_size)
    max_contributor = int(max_contributor)
    valid_rate = float(valid_rate)

    status = 'STANDBY'

    project = Project.objects.create(uid=uid,owner=user,
        max_contributor=max_contributor,status=status, max_step = int(total_task/step_size),
        step_size = step_size, epoch = epoch, batch_size = batch_size, valid_rate = valid_rate)


    numpy_file = request.FILES.get('weight', INVALID)

    if(numpy_file == INVALID):
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Numpy data"
        })

    init_weight = np.load(request.FILES.get('weight'),allow_pickle = True)

    schedule_manager.init_project(project_id=uid,total_step=total_task,step_size=step_size,
        weight=init_weight, epoch=epoch, batch_size = batch_size, max_contributor=max_contributor)

    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
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
        project = Project.objects.get(uid=project_uid)
        project.status = 'started'
        project.started_at = timezone.now()
        project.save()
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


# 아래와 같은 형태로 data 받음
# {
#     "project_uid":"",
#     "data":"",
#     "label":""
# }
def get_data_url(request):
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

    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    data = request.POST.get('data', '')
    label = request.POST.get('label', '')
    index = request.POST.get('index', '')
    project_uid = request.POST.get('project_uid', '')
    bucket_name='daig'

    project=Project.objects.get(uid=project_uid)

    task=Task.objects.create(uid=(project.uid+str(index)), project=project)
    task.data_url=f'project/{project_uid}/task/{task.uid}/{data}'
    task.label_url=f'project/{project_uid}/task/{task.uid}/{label}'

    task.save()

    data_url=s3.generate_presigned_url("put_object",Params={
        'Bucket':bucket_name,
        'Key':task.data_url
    }, ExpiresIn=3600)

    label_url=s3.generate_presigned_url("put_object",Params={
        'Bucket':bucket_name,
        'Key':task.label_url
    }, ExpiresIn=3600)
    
    return JsonResponse({
        "is_succesful":True,
        "data_url":data_url,
        "label_url":label_url,
    })

# 아래와 같은 형태로 data 받음
# {
#     "project_uid":"",
#     "model":"",
# }
def get_model_url(request):
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

    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    model = request.POST.get('model', '')
    project_uid = request.POST.get('project_uid', '')
    bucket_name='daig'

    project=Project.objects.get(uid=project_uid)
    project.model_url=f'project/{project_uid}/model/{model}'
    project.save()

    url=s3.generate_presigned_url("put_object",Params={
        'Bucket':bucket_name,
        'Key':project.model_url
    }, ExpiresIn=3600)

    return JsonResponse({
        "is_succesful":True,
        "model_url":url
    })

def get_model_url_for_learnig(request, project_uid):
    if request.method!='GET':
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
            "state":"good",
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
        ########################

        service_name = 's3'
        endpoint_url = 'https://kr.object.ncloudstorage.com'
        region_name = 'kr-standard'
        access_key = '0C863406F8D54433789F'
        secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'
        bucket_name='daig'
        s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)
        project=Project.objects.get(uid=project_uid)

        epoch = project.epoch
        batch_size = project.batch_size
        valid_rate = project.valid_rate

        url=s3.generate_presigned_url("get_object",Params={
            'Bucket':bucket_name,
            'Key':project.model_url
        }, ExpiresIn=3600)
        
        task_uid = project.uid+str(task_index)

        task=Task.objects.get(uid=task_uid)
        data_url=task.data_url
        label_url=task.label_url

        if(task.uid == None):
            return JsonResponse({
            "is_successful":False,
            "project_uid":project_uid,
            "message":"Wrong task index"
        })

        data_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':bucket_name,
            'Key':data_url
        }, ExpiresIn=3600)

        label_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':bucket_name,
            'Key':label_url
        }, ExpiresIn=3600)
        
        #######################
        return JsonResponse({
            "is_successful":True,
            "project_uid":project_uid,
            "task_index":task_index,
            "total_task":total_task_number,
            "message":"Available task found",
            "model_url":url,
            "data_url":data_url,
            "label_url":label_url,
            "epoch": epoch,
            "batch_size": batch_size,
            "valid_rate": valid_rate
        })
    else:
        return JsonResponse({
            "is_successful":False,
            "project_uid":project_uid,
            "message":"No available task"
        })


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
    spent_time = float(request.POST.get('spent_time', '5'))
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
        "is_successful":True,
        "state":"expired",
        "message":"Gradient Update fail. expired index"
        })

    if(_is_project_finished(project_id=project_uid)):
        service_name = 's3'
        endpoint_url = 'https://kr.object.ncloudstorage.com'
        region_name = 'kr-standard'
        access_key = '0C863406F8D54433789F'
        secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'
        bucket_name='daig'
        s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)
        project=Project.objects.get(uid=project_uid)

        url=s3.generate_presigned_url("put_object",Params={
            'Bucket':bucket_name,
            'Key':f'project/{project_uid}/model/result.npy'
        }, ExpiresIn=3600)
        
        with TemporaryFile() as tf:
            np.save(tf, np.array(_get_project_result(project_id=project_uid),dtype=object))
            _ = tf.seek(0)
            requests.put(url=url,data=tf)

        project = Project.objects.get(uid=project_uid)
        project.status = 'finished'
        project.finished_at = timezone.now()
        project.save()

    return JsonResponse({
        "is_successful":True,
        "message":"Gradient Updated Success"
    })

def get_owned_projects(request):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

    key = request.META.get('HTTP_AUTH')
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })
    user=User.objects.get(key=key)
    projects=Project.objects.filter(owner=user).all()
    projects=[{
        'project_uid':p.uid,
        'progress':'미구현',
        'status':p.status,
        'created_at':str(p.created_at)
    } for p in projects]
    return JsonResponse({
        'is_successful':True,
        'projects':projects
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

def _get_project_result(project_id):
    return schedule_manager.get_project_result(project_id=project_id)

def _start_task(project_id, task_id):
    schedule_manager.start_project_task(project_id=project_id, task_no=task_id)

def _update_project(project_id, task_id, gradient, time):
    return schedule_manager.update_project(project_id=project_id, task_no=task_id, gradient=gradient, time = time)
    
def _is_project_finished(project_id):
    return schedule_manager.is_project_finished(project_id=project_id)

def _load_projects_from_DB():
    schedule_manager.reset()
    project_list = Project.objects.all()

    if(not(project_list.exists())):
        return -1

    for project in project_list:
        schedule_manager.init_project(project_id=project.uid,total_step=project.max_step,
            step_size=project.step_size)

    return 1
    # gonna do this far later


