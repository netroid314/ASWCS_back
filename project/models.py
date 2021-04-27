from django.db import models
from django.contrib import admin
from django.conf import settings
from bson.objectid import ObjectId
from django.contrib.auth import get_user_model

class Project (models.Model):
    uid = models.CharField(
        max_length=200, 
        default=str(ObjectId()),
        primary_key=True
    )
    owner=models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rrs_url=models.TextField()
    model_url=models.TextField()
    max_contributor=models.IntegerField()
    status=models.CharField(max_length=10)
    created_at = models.DateTimeField('created_at')
    started_at=models.DateTimeField('started_at')
    finished_at=models.DateTimeField('finished_at')

    def __str__(self):
        return self.uid
    


class Task (models.Model):
    uid = models.CharField(
        max_length=200, 
        default=str(ObjectId()),
        primary_key=True
    )
    tasker=models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    project=models.ForeignKey(Project, on_delete=models.CASCADE)
    credit=models.IntegerField()
    status=models.CharField(max_length=10)
    started_at=models.DateTimeField('started_at')
    finished_at=models.DateTimeField('finished_at')

    def __str__(self):
        return self.uid


class Contribution (models.Model):
    project=models.ForeignKey(Project, on_delete=models.CASCADE)
    tasker=models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task_count=models.IntegerField()

# Create your models here.
