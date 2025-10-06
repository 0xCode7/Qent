from django.contrib import admin
from .models import Car, Brand, Review


# Register your models here.
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    pass

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass