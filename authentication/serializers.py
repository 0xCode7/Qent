from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from rest_framework import serializers
from django.conf import settings

import os, json

COUNTRIES_FILE = os.path.join(settings.BASE_DIR, 'authentication/data/countries.json')
with open(COUNTRIES_FILE, 'r', encoding='utf-8') as f:
    COUNTRIES = json.load(f)
COUNTRY_CODES = [c["abbreviation"] for c in COUNTRIES]


class CountrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    country = serializers.CharField()
    abbreviation = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = ['id', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    country = serializers.CharField()

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'country']

    def validate_country(self, value):
        if value not in COUNTRY_CODES:
            raise serializers.ValidationError("Invalid country code")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user_obj = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"login_error": ["User not found"]})

        user = authenticate(username=user_obj.username, password=data["password"])
        if not user:
            raise serializers.ValidationError({"login_error": ["Wrong password"]})
        refresh = RefreshToken.for_user(user)
        return {
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }


class PhoneVerificationRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()


class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate_code(self, value):
        if value != os.getenv("VERIFICATION_CODE"):
            raise serializers.ValidationError("Invalid verification code")
        return value
