from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Location


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_country', 'get_phone']

    def get_country(self, obj):
        return obj.profile.country if hasattr(obj, 'profile') else "-"
    get_country.short_description = 'Country'

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else "-"
    get_phone.short_description = 'Phone'

admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone','phone_is_verified', 'country', 'available_to_create_car']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
