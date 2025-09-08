from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    full_name = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=3, default='PS')
    phone_verified = models.BooleanField(default=False)