from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User=get_user_model()

class CreditLog(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    action=models.CharField(max_length=10)
    details=models.TextField()
    amount=models.IntegerField()
    date=models.DateTimeField(default=timezone.now())

# Create your models here.
