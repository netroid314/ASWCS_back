from django.db import models
from django.contrib import admin
from bson.objectid import ObjectId

class Project (models.Model):
    uid = models.CharField(max_length=200, default=str(ObjectId()))
    hello=models.CharField(max_length=200)
    world=models.CharField(max_length=200)
    here=models.CharField(max_length=200)
    created_at = models.DateTimeField('created_at')


# Create your models here.
