import math
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Car, Review, Brand
from .serializers import CarSerializer, ReviewSerializer, BrandSerializer


def haversine(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# List all cars
class CarListView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


# Retrieve car details (with reviews)
class CarDetailView(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


# Add a review
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        car_id = self.kwargs.get("car_id")
        serializer.save(user=self.request.user, car_id=car_id)


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BestCarsListView(generics.ListAPIView):
    queryset = Car.objects.order_by('-average_rate')[:6]
    serializer_class = CarSerializer



class NearestCarListView(generics.ListAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.location:
            return Car.objects.none()  # If user has no location

        user_lat = float(user.location.lat)
        user_lng = float(user.location.lng)

        cars = Car.objects.all()
        # Create a list of tuples (car, distance)
        car_with_distance = [
            (car, haversine(user_lat, user_lng, car.location.lat, car.location.lng))
            for car in cars if car.location
        ]

        # Sort by distance
        car_with_distance.sort(key=lambda x: x[1])

        # Return the nearest 5 cars as a queryset
        nearest_cars_ids = [c[0].id for c in car_with_distance[:10]]
        return Car.objects.filter(id__in=nearest_cars_ids)
