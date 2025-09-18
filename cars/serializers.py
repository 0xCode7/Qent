from rest_framework import serializers

from authentication.serializers import LocationSerializer
from .models import Brand, Color, CarFeature, Car, Review


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

    class Meta:
        model = Review
        fields = ["id", "username", "review", "rate"]


class CarSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    car_features = CarFeatureSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    location = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = [
            "id", "name", "image", "description",
            "brand", "color", "car_features",
            "location", "average_rate", "price_per_day",
            "available_to_book", "reviews", 'location'
        ]
    def get_location(self, obj):
        if obj.location:
            return LocationSerializer(obj.location).data
        return None