import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
def default_location():
    return {"lat": 30.0444, "lng": 31.2357}


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    lat = models.FloatField()
    lng = models.FloatField()


    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"Qent-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=3, default='PS')
    phone = models.CharField(max_length=20, null=False, blank=False, default='')
    phone_is_verified = models.BooleanField(default=False)
    reset_code = models.CharField(max_length=4, null=True, blank=True)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, default=1)
    available_to_create_car = models.BooleanField(default=False)
