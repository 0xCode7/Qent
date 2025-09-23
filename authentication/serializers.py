from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import User, Profile, Location
from rest_framework import serializers
from django.conf import settings
import os, json

COUNTRIES_FILE = os.path.join(settings.BASE_DIR, 'authentication/data/countries.json')
with open(COUNTRIES_FILE, 'r', encoding='utf-8') as f:
    COUNTRIES = json.load(f)
COUNTRY_CODES = [c["id"] for c in COUNTRIES]


class CountrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    country = serializers.CharField()
    abbreviation = serializers.CharField()


class LocationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class UserSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    phone_is_verified = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'phone_is_verified',
            'country',
            'location'
        ]
        read_only_fields = ['id', 'email']

    def get_full_name(self, obj):
        return obj.profile.full_name if hasattr(obj, "profile") else None

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, "profile") else None

    def get_phone_is_verified(self, obj):
        return obj.profile.phone_is_verified if hasattr(obj, "profile") else False

    def get_country(self, obj):
        """
        Map stored country code -> full country object using CountrySerializer
        """
        if hasattr(obj, "profile") and obj.profile.country:
            country_obj = next(
                (c for c in COUNTRIES if c["abbreviation"] == obj.profile.country), None
            )
            if country_obj:
                return CountrySerializer(country_obj).data
        return None

    def get_location(self, obj):
        if hasattr(obj, "profile") and obj.profile.location:
            return LocationSerializer(obj.profile.location).data
        return None


class ProfileSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)  # for output
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True,
        required=False
    )
    country = serializers.SerializerMethodField()
    country_id = serializers.IntegerField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)  # add email here

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "email",
            "phone",
            "phone_is_verified",
            "location",
            "location_id",
            'country',
            "country_id",
            "available_to_create_car",
        ]
        read_only_fields = ["phone_is_verified"]

    def get_country(self, obj):
        country_obj = next((c for c in COUNTRIES if c["abbreviation"] == obj.country), None)
        if country_obj:
            return CountrySerializer(country_obj).data
        return None

    def update(self, instance, validated_data):
        new_phone = validated_data.get("phone")
        if new_phone and new_phone != instance.phone:
            instance.phone_is_verified = False

        # Handle country
        country_id = validated_data.pop("country_id", None)
        if country_id:
            country_obj = next((c for c in COUNTRIES if c["id"] == country_id), None)
            if not country_obj:
                raise serializers.ValidationError({"country_id": "Invalid country ID"})
            validated_data["country"] = country_obj["abbreviation"]

        # Handle User updates (email, full_name, etc.)
        user = instance.user
        email = validated_data.pop("email", None)
        if email:
            user.email = email

        full_name = validated_data.pop("full_name", None)
        if full_name:
            user.full_name = full_name

        user.save()

        # Now update only Profile fields
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        user_data = UserSerializer(instance.user).data
        profile_data = super().to_representation(instance)
        merged = {**user_data, **profile_data}
        return {"data": merged}


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    country_id = serializers.IntegerField(write_only=True)
    location_id = serializers.IntegerField(write_only=True)
    available_to_create_car = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password', 'country_id', 'location_id', 'available_to_create_car']

    def validate_country_id(self, value):
        """Ensure the country ID exists and return abbreviation."""
        country_obj = next((c for c in COUNTRIES if c["id"] == value), None)
        if not country_obj:
            raise serializers.ValidationError("Invalid country ID")
        return country_obj["abbreviation"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        country_abbr = validated_data.pop("country_id")  # store abbreviation
        location_id = validated_data.pop("location_id")
        full_name = validated_data.pop("full_name")
        phone = validated_data.pop("phone")
        available_to_create_car = validated_data.pop("available_to_create_car", False)

        # create user
        user = User(email=validated_data["email"])
        user.set_password(password)
        user.save()

        # update profile
        profile = user.profile
        profile.full_name = full_name
        profile.phone = phone
        profile.country = country_abbr
        profile.location_id = location_id
        profile.available_to_create_car = available_to_create_car
        profile.save()

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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField()
    reset_token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"message": "Passwords do not match"})

        token = AccessToken(data['reset_token'])

        try:
            user = User.objects.get(id=token['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User does not exist"})

        if user.profile.reset_code != data["code"]:
            raise serializers.ValidationError({"message": "Invalid reset code"})

        # verify token
        if user.profile.reset_token != str(token):
            raise serializers.ValidationError({"message": "Invalid reset token"})

        return data


class PhoneVerificationRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()


class PhoneVerificationSerializer(serializers.Serializer):
    code = serializers.CharField()
    verify_token = serializers.CharField()
