from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as geo_models

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from PIL import Image

class Registration(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(blank=False,max_length=10)
    
    def __str__(self):
        return self.user.username
    