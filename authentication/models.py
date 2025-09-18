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
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=3, default='PS')
    phone = models.CharField(max_length=20, null=False, blank=False, default='')
    phone_is_verified = models.BooleanField(default=False)
    reset_code = models.CharField(max_length=4, null=True, blank=True)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, default=1)

    def save(self, *args, **kwargs):
        if not self.username:
            # Generate something like Qent-a1b2c3
            self.username = f"Qent-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
