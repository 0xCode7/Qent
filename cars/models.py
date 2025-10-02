from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import User, Location
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import os




def car_image_upload_path(instance, filename):
    brand_slug = slugify(instance.car.brand.name)
    model_slug = slugify(instance.car.name)
    return f"cars/{brand_slug}/{model_slug}/{filename}"


# -------------------- MODELS --------------------

class CarFeature(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    image = models.ImageField(upload_to='icons/')
    value = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Color(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    hex_value = models.CharField(max_length=8, null=False, blank=False)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.name


class Car(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255)
    TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('luxury', 'Luxury'),
    ]
    car_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='regular')

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cars")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="cars")
    car_features = models.ManyToManyField(CarFeature, related_name="cars")
    seating_capacity = models.PositiveSmallIntegerField(null=True, blank=True, default='4')
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    average_rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    is_for_rent = models.BooleanField(default=False)
    daily_rent = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2)
    weekly_rent = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2)
    monthly_rent = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2)
    yearly_rent = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2)

    is_for_pay = models.BooleanField(default=False)
    price = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2)

    available_to_book = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=car_image_upload_path)

    def __str__(self):
        return f"Image for {self.car.name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")  # ✅ link to car
    review = models.CharField(max_length=255, null=False, blank=False)
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.car.name} ({self.rate})"
