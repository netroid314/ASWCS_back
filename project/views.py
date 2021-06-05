from datetime import time
import math
from botocore.configprovider import SectionConfigProvider
from django.shortcuts import render, resolve_url
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from ..credit.models import *
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

BUCKET_NAME = 'DAIG'

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
    parameter_number = request.POST.get('parameter_number','0')

    total_task = int(total_task)
    step_size = int(step_size)
    epoch = int(epoch)
    batch_size = int(batch_size)
    max_contributor = int(max_contributor)
    valid_rate = float(valid_rate)
    parameter_number = int(parameter_number)

    credit = _calculate_credit(parameter_number=parameter_number,epoch=epoch,
        batch_size=batch_size, total_task=total_task)

    status = 'STANDBY'

    project = Project.objects.create(uid=uid,owner=user,
        max_contributor=max_contributor,status=status, max_step = int(total_task/step_size),
        created_at = timezone.now(),
        step_size = step_size, epoch = epoch, batch_size = batch_size, valid_rate = valid_rate,
        credit = credit)

    numpy_file = request.FILES.get('weight', INVALID)

    if(numpy_file == INVALID):
        return JsonResponse({
            "is_successful":False,
            "message":"Invalid Numpy data"
        })

    init_weight = np.load(request.FILES.get('weight'),allow_pickle = True)

    schedule_manager.init_project(project_id=uid,total_step=total_task,step_size=step_size,
        weight=init_weight, epoch=epoch, batch_size = batch_size, max_contributor=max_contributor, credit=credit)

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
    
    project = Project.objects.get(uid=project_uid)

    if(project.exists()):
        project.status='INPROGRESS'
        project.status = 'started'
        project.started_at = timezone.now()
        project.save()

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

    s3 = _get_boto3()

    data = request.POST.get('data', '')
    label = request.POST.get('label', '')
    index = request.POST.get('index', '')
    project_uid = request.POST.get('project_uid', '')

    project=Project.objects.get(uid=project_uid)

    task=Task.objects.create(uid=(project.uid+str(index)), credit = project.credit, project=project)

    task.data_url=f'project/{project_uid}/task/{task.uid}/{data}'
    task.label_url=f'project/{project_uid}/task/{task.uid}/{label}'

    task.save()

    data_url=s3.generate_presigned_url("put_object",Params={
        'Bucket':BUCKET_NAME,
        'Key':task.data_url
    }, ExpiresIn=3600)

    label_url=s3.generate_presigned_url("put_object",Params={
        'Bucket':BUCKET_NAME,
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

    s3 = _get_boto3()

    model = request.POST.get('model', '')
    project_uid = request.POST.get('project_uid', '')

    project=Project.objects.get(uid=project_uid)
    project.model_url=f'project/{project_uid}/model/{model}'
    project.save()
    url=s3.generate_presigned_url("put_object",Params={
        'Bucket':BUCKET_NAME,
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


def is_project_finished(request, project_uid):
    if request.method!='GET':
        return HttpResponse(status = '270')

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    if schedule_manager.is_project_finished(project_id = project_uid):
        return HttpResponse(status = '200')

    return HttpResponse(status = '270')

def get_project_result(request, project_uid):
    if request.method!='GET':
        return HttpResponse(status = '270')

    key = request.META.get('HTTP_AUTH')
    authorization_result = check_authorization(key)
    if(authorization_result): return authorization_result

    if schedule_manager.is_project_finished(project_id = project_uid):
        s3 = _get_boto3()

        project = Project.objects.get(uid = project_uid)

        model_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':project.model_url
        }, ExpiresIn=3600)

        result_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':project.result_url
        }, ExpiresIn=3600)
    
        return JsonResponse({
            "is_successful": True,
            "model_url": model_url,
            "result_url": result_url
        })

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
        target_project.status='STANDBY'
        target_project.save()
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
        
# def get_project_progress(request, project_uid):
#     return None

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
        s3 = _get_boto3()

        project=Project.objects.get(uid=project_uid)

        epoch = project.epoch
        batch_size = project.batch_size
        valid_rate = project.valid_rate

        url=s3.generate_presigned_url("get_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':project.model_url
        }, ExpiresIn=3600)

        task=Task.objects.get(uid=project.uid+str(task_index))
        data_url=task.data_url
        label_url=task.label_url
        task.save()

        if(task.uid == None):
            return JsonResponse({
            "is_successful":False,
            "project_uid":project_uid,
            "message":"Wrong task index"
        })

        data_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':data_url
        }, ExpiresIn=3600)

        label_url=s3.generate_presigned_url("get_object",Params={
            'Bucket':BUCKET_NAME,
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
        task = Task.objects.get(uid = project_uid + str(task_index))
        task.status = 'started'
        task.started_at = timezone.now()
        task.save()

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

    credit_amout = Project.objects.get(uid=project_uid).credit

    gradient = np.load(numpy_file,allow_pickle = True)

    result = _update_project(project_id=project_uid,task_id=task_index,gradient=gradient, time = spent_time)
    if(result == INVALID):
        return JsonResponse({
        "is_successful":True,
        "state":"expired",
        "message":"Gradient Update fail. expired index"
        })

    if(result == 0):
        s3 = _get_boto3()

        project=Project.objects.get(uid=project_uid)
        project.save_url = f'project/{project_uid}/model/save.npy'
        project.current_step = schedule_manager.get_current_step(project_id=project_uid)
        project.save()

        url=s3.generate_presigned_url("put_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':project.save_url
        }, ExpiresIn=3600)

        with TemporaryFile() as tf:
            np.save(tf, np.array(_get_project_result(project_id=project_uid),dtype=object))
            _ = tf.seek(0)
            requests.put(url=url,data=tf)

    if(_is_project_finished(project_id=project_uid)):
        s3 = _get_boto3()

        project=Project.objects.get(uid=project_uid)
        project.result_url = f'project/{project_uid}/model/result.npy'

        url=s3.generate_presigned_url("put_object",Params={
            'Bucket':BUCKET_NAME,
            'Key':project.result_url
        }, ExpiresIn=3600)
        
        with TemporaryFile() as tf:
            np.save(tf, np.array(_get_project_result(project_id=project_uid),dtype=object))
            _ = tf.seek(0)
            requests.put(url=url,data=tf)

        project.status = 'FINISHED'
        project.finished_at = timezone.now()

    project.save()

    task = Task.objects.get(uid = project.uid+str(task_index))
    task.status = 'finised'
    task.inished_at = timezone.now()
    task.save()

    if(not create_credit_log(case=2,userKey=key,amount=credit_amout)):
        return JsonResponse({
            "is_successful":True,
            "message":"Gradient Updated Success but Credit error occured :("
        })

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

    projects_json=[{
        'project_uid':p.uid,
        'progress':schedule_manager.get_project_progress(p.uid),
        'status':p.status,
        'created_at':str(p.created_at)
    } for p in projects]

    return JsonResponse({
        'is_successful':True,
        'projects':projects_json
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


def create_credit_log(case, userKey, amount):
    
    user = User.objects.get(key=userKey)

    if (case==1):
        details = '크레딧 충전'
        action='+'
        user.credit += amount

    elif(case==2):
        details = '자원 제공'
        action='+'
        user.credit += amount

    elif(case==3):
        details = '프로젝트 비용'
        action='-'
        user.credit -= amount

    else:
        return False
    
    user.save()

    credit_log=CreditLog.objects.create(user=user,
    action=action , details=details, amount=amount,
    date= timezone.localtime(timezone.now()).strftime('%Y-%m-%d'))
    credit_log.save()

    return True


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

def _calculate_credit(parameter_number, epoch, batch_size, total_task):
    param_convt = math.log10(parameter_number)
    batch_convt = math.log2(batch_size)
    epoch_convt = epoch/10

    credit = (2**param_convt) * max(batch_convt-3,1) * epoch_convt * 10
    credit = credit/total_task

    return credit

def _load_projects_from_DB():
    schedule_manager.reset()
    project_list = Project.objects.filter(status = 'INPROGRESS')

    if(not(project_list.exists())):
        return -1

    for project in project_list:
        schedule_manager.init_project(project_id=project.uid, total_step=project.max_step,
            step_size=project.step_size)
        schedule_manager.restore(project_id=project.uid, saved_step = project.current_step)

    return 1
    # gonna do this far later

def _get_boto3():
    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    access_key = '0C863406F8D54433789F'
    secret_key = 'CC66B33F3B1487B10DF50F82638B4065CD4723B0'

    return boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)