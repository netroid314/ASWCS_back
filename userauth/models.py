from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models 
from django.utils import timezone

class UserManager(BaseUserManager):    
    
    use_in_migrations = True    
    
    def create_user(self, username, password=None):        
     
        user = self.model(                      
            username = username        
        )        
        user.set_password(password)        
        user.save(using=self._db)        
        return user     
    def create_superuser(self, username,password ):        
       
        user = self.create_user(                   
            username = username,            
            password=password        
        )        
        user.is_admin = True        
        user.is_superuser = True        
        user.is_staff = True        
        user.save(using=self._db)        
        return user 

        
class User(AbstractBaseUser,PermissionsMixin):    
    
    objects = UserManager()
    
    user_SN=models.CharField(
        max_length=200,
        editable=False,
        unique=True,
        primary_key=True
    )

    username = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    email=models.EmailField(
        max_length=254
    )

    credit=models.PositiveIntegerField(
        default=0
    )

    key = models.CharField(
        max_length=200,
        unique=True
    )


    is_active = models.BooleanField(default=True)    
    is_admin = models.BooleanField(default=False)    
    is_superuser = models.BooleanField(default=False)    
    is_staff = models.BooleanField(default=False)     
    date_joined = models.DateTimeField(default=timezone.now())     
    USERNAME_FIELD = 'username'    




# Create your models here.
