from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create',create_project),
    path('<str:project_uid>/upload',upload_data),
    path('<str:project_uid>/start',start_project),
    path('<str:project_uid>/result',get_project_result),
    path('<str:project_uid>/pause',pause_project),
    path('<str:project_uid>/progress',get_project_progress),
]