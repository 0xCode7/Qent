from django.db import models
from authentication.models import User

# Create your models here.
class CarFeature(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    image = models.ImageField(upload_to='icons/')
    value = models.CharField(max_length=255, null=False, blank=False)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.CharField(max_length=255, null=False, blank=False)
    rate = models.IntegerField(max_length=5)


class Color(models.CharField):
    name = models.CharField(max_length=50, null=False, blank=False)
    hex_value = models.CharField(max_length=8, null=False, blank=False)


class Car(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='cars/')
