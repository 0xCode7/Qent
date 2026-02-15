from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg
from rest_framework import serializers
from .models import Brand, Color, CarFeature, Car, Review, CarImage
from authentication.serializers import LocationSerializer, UserSerializer



class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "image"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "hex_value"]


class CarFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFeature
        fields = ["id", "name", "value", "image"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.name.lower() in ['seating_capacity', 'seats']:
            try:
                count = int(instance.value)
                data['value'] = f"{count} Seats" if count > 1 else "1 Seat"
            except ValueError:
                data['value'] = instance.value
        return data


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_image = serializers.ImageField(source="user.profile.image", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "username", "review", "user_image", "rate"]


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image']


class CarSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    car_features = CarFeatureSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    images = CarImageSerializer(many=True, read_only=True)
    first_image = serializers.SerializerMethodField(read_only=True)
    seating_capacity = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    reviews_avg = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = [
            "id", "name", "description", "owner", "first_image", "images", "car_type",
            "brand", "color", "car_features", "seating_capacity",
            "location", "average_rate",
            "is_for_rent", "daily_rent", "weekly_rent", "monthly_rent", "yearly_rent",
            "is_for_pay", "price",
            "available_to_book", "reviews", "reviews_count", "reviews_avg"
        ]

    def get_location(self, obj):
        if obj.location:
            return LocationSerializer(obj.location).data
        return None

    def get_first_image(self, obj):
        first_img = obj.images.first()
        request = self.context.get('request')

        if first_img and first_img.image:
            image_url = first_img.image.url
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return None

    def get_seating_capacity(self, obj):
        if obj.seating_capacity:
            return f"{obj.seating_capacity} Seats" if obj.seating_capacity > 1 else "1 Seat"

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_reviews_avg(self, obj):
        avg = obj.reviews.aggregate(avg=Avg("rate"))["avg"] or 0
        return round(avg, 1)

    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:3]
        return ReviewSerializer(reviews, many=True, context=self.context).data

    def validate(self, attrs):
        car = self.instance
        if attrs.get('is_for_rent') is True:
            today = timezone.now().date()

            if not car.subscription_end or car.subscription_end < today:
                raise serializers.ValidationError({"message":
                    "Car is not available for rent."
                })

        return attrs
class CarDetailsSerializer(CarSerializer):
    owner = UserSerializer(read_only=True)


class CarSubscriptionSerializer(serializers.Serializer):
    @transaction.atomic
    def save(self, **kwargs):
        request = self.context['request']
        car = self.context['car']
        profile = request.user.profile

        # Should be the owner
        if car.owner != request.user:
            raise serializers.ValidationError({"message": "You should be the owner of this car."})

        # Already Subscribed?
        today = timezone.now().date()
        if car.subscription_end and car.subscription_start >= today:
            raise serializers.ValidationError({"message":"Car already has active subscription."})

        # Check for the balance
        if profile.balance < 10:
            raise serializers.ValidationError({"message": "Insufficient balance."})

        profile.balance -= 10
        profile.save()


        #Subscribe
        car.is_subscribed = True
        car.subscription_start = today
        car.subscription_end = today + timedelta(days=30)
        car.save()

        return car
