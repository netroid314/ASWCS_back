from django.db import models
from django.contrib import admin
from django.conf import settings
from bson.objectid import ObjectId
from django.contrib.auth import get_user_model
from django.utils import timezone

class Project (models.Model):
    uid = models.CharField(
        max_length=200, 
        default=str(ObjectId()),
        primary_key=True
    )
    owner=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    max_contributor=models.IntegerField(null=True, blank=True)
    model_url=models.TextField(null=True, blank=True)
    status=models.CharField(max_length=20,default="not_started")
    created_at = models.DateTimeField('created_at',default=timezone.now())
    started_at=models.DateTimeField('started_at',null=True, blank=True)
    finished_at=models.DateTimeField('finished_at',null=True, blank=True)

    def __str__(self):
        return self.uid
    


class Task (models.Model):
    uid = models.CharField(
        max_length=200, 
        primary_key=True
    )
    index=models.TextField(null=True, blank=True)
    tasker=models.ForeignKey(get_user_model(), on_delete=models.CASCADE,null=True, blank=True)
    project=models.ForeignKey(Project, on_delete=models.CASCADE)
    data_url=models.TextField(null=True, blank=True)
    label_url=models.TextField(null=True, blank=True)
    credit=models.IntegerField(null=True, blank=True)
    status=models.CharField(max_length=20,default="not_started")
    started_at=models.DateTimeField('started_at',null=True, blank=True)
    finished_at=models.DateTimeField('finished_at',null=True, blank=True)

    def __str__(self):
        return self.uid


class Contribution (models.Model):
    project=models.ForeignKey(Project, on_delete=models.CASCADE)
    tasker=models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task_count=models.IntegerField(null=True, blank=True)

# Create your models here.
