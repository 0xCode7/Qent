from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import User, Location
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import os


def car_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    name_slug = slugify(instance.name)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{name_slug}_{timestamp}.{ext}"

    # ✅ Store inside /media/cars/<brand-name>/
    return os.path.join("cars", slugify(instance.brand.name), new_filename)


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
    image = models.ImageField(upload_to=car_image_upload_path)
    description = models.CharField(max_length=255)

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cars")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="cars")
    car_features = models.ManyToManyField(CarFeature, related_name="cars")

    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    average_rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    is_for_rent = models.BooleanField(default=False)
    daily_rent = models.FloatField(null=True, blank=True)
    weekly_rent = models.FloatField(null=True, blank=True)
    monthly_rent = models.FloatField(null=True, blank=True)
    yearly_rent = models.FloatField(null=True, blank=True)

    is_for_pay = models.BooleanField(default=False)
    price = models.FloatField(null=True, blank=True)

    available_to_book = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")  # ✅ link to car
    review = models.CharField(max_length=255, null=False, blank=False)
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.car.name} ({self.rate})"
