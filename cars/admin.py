from django.contrib import admin
from .models import Car, Brand


# Register your models here.
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    pass

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass