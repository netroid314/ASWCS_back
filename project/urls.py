from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create',create_project),
    path('upload',get_upload_url),
    path('<str:project_uid>/start',start_project),
    path('<str:project_uid>/result',get_project_result),
    path('<str:project_uid>/status',change_project_status),
    path('<str:project_uid>/progress',get_project_progress),
]