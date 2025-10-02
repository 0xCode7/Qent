from rest_framework import serializers
from django.db.models import Avg, Count
from authentication.serializers import LocationSerializer
from .models import Brand, Color, CarFeature, Car, Review, CarImage


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

    reviews_count = serializers.SerializerMethodField()
    reviews_avg = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = [
            "id", "name", "description", "first_image", "images", "car_type",
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
        return first_img.image.url if first_img else None

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_reviews_avg(self, obj):
        return obj.reviews.aggregate(avg=Avg("rate"))["avg"] or 0

    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:3]
        return ReviewSerializer(reviews ,many=True).data