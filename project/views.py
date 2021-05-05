from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from .models import *
import boto3
import json

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

    key = eval(request.META.get('HTTP_AUTH')).get("key")
    if User.objects.filter(key=key).exists()==False:
        return JsonResponse({
            "is_successful":False,
            "message":"Expired key. Please Login again."
        })

    user=User.objects.get(key=key)

    project=Project.objects.create(owner=user)
    project.save()
    return JsonResponse({
        "is_successful":True,
        "project_uid":project.uid,
        "message":"Project successfully created."
    })


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

def start_project(request, project_uid): 


    return JsonResponse({"test":"success"})

def get_project_result(request, project_uid): 
     

    return JsonResponse({"test":"success"})

def change_project_status(request, project_uid):
    return None

def get_project_progress(request, project_uid):
    return None

def get_task(request):
    if request.method!='GET':
        return JsonResponse({
            "is_successful":False,
            "message":"[ERROR] GET ONLY"
        })

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
