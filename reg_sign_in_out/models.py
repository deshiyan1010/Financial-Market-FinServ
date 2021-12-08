from django.db import models
from django.contrib.auth.models import User



class Registration(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(blank=False,max_length=10)
    
    def __str__(self):
        return self.user.username
    