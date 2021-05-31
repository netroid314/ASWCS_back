from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/',create_project),
    path('data/upload',get_data_url),
    path('model/upload',get_model_url),
    path('owned/',get_owned_projects),
    path('<str:project_uid>/start/',start_project),
    path('<str:project_uid>/finished',is_project_finished),
    path('<str:project_uid>/result',get_project_result),
    path('<str:project_uid>/pause/',pause_project),

    path('<str:project_uid>/project/weight',get_project_weight),
    path('get/project',get_available_project),
    path('<str:project_uid>/task/get',get_task_index),
    path('<str:project_uid>/task/start/',start_project_task),
    path('<str:project_uid>/task/update/',update_project_task),
]