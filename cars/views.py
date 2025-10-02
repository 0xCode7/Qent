import math
from django.db.models import Q, Min, Max
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


# Get all reviews
class GetAllReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        car_id = self.kwargs.get('car_id')
        return Review.objects.filter(car_id=car_id).select_related("user__profile")


# Add a review
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        car_id = self.kwargs.get("car_id")
        serializer.save(user=self.request.user, car_id=car_id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Review added successfully",
                "review": response.data
            },
            status=status.HTTP_201_CREATED
        )


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BrandDetailsView(generics.RetrieveAPIView):
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
        if not user.profile.location:
            return Car.objects.none()  # If user has no location

        user_lat = float(user.profile.location.lat)
        user_lng = float(user.profile.location.lng)

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


class CarSearchView(generics.ListAPIView):
    serializer_class = CarSerializer

    def get_queryset(self):
        queryset = Car.objects.all()
        params = self.request.query_params

        # ----- Keyword search -----
        search = params.get('query')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(color__name__icontains=search)
            )

        # ----- Car Type -----
        car_type = params.get('car_type')
        if car_type:
            queryset = queryset.filter(car_type__iexact=car_type)

        # ----- Sale Type -> Rent / Pay / Both -----
        sale_type = params.get('type')
        min_price = params.get('min_price')
        max_price = params.get('max_price')

        if sale_type == "rent":
            queryset = queryset.filter(is_for_rent=True)
            rental_time = params.get('rental_time')  # 'daily', 'weekly', 'monthly', 'yearly'
            if rental_time:
                rental_field = f"{rental_time}_rent"
                queryset = queryset.filter(**{f"{rental_field}__isnull": False})
                if min_price:
                    queryset = queryset.filter(**{f"{rental_field}__gte": float(min_price)})
                if max_price:
                    queryset = queryset.filter(**{f"{rental_field}__lte": float(max_price)})

        elif sale_type == "pay":
            queryset = queryset.filter(is_for_pay=True)
            if min_price:
                queryset = queryset.filter(price__gte=float(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=float(max_price))

        elif sale_type == "rent_pay":
            queryset = queryset.filter(Q(is_for_rent=True) | Q(is_for_pay=True))

        # ----- Location -----
        location_id = params.get('location_id')
        if location_id:
            queryset = queryset.filter(location__id=location_id)

        # ----- Color -----
        color_id = params.get('color_id')
        if color_id:
            queryset = queryset.filter(color__id=color_id)

        # ----- Seating Capacity -----
        seats = params.get('seating_capacity')
        if seats:
            queryset = queryset.filter(seating_capacity__gte=int(seats))

        # ----- Fuel Type (CarFeature) -----
        fuels = params.getlist('fuel_type')
        if fuels:
            queryset = queryset.filter(
                car_features__name="Fuel Type",
                car_features__value__in=fuels
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No results found"}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APISettings(APIView):
    def get(self, request):
        def get_price_range():
            # 1. get min and max prices
            price_stats = Car.objects.aggregate(
                min_price=Min("price"),
                max_price=Max("price")
            )

            min_price = price_stats["min_price"] or 0
            max_price = price_stats["max_price"] or 0

            if max_price == 0:
                return Response({"price_distribution": [], "min_price": 0, "max_price": 0})

            # 2. number of buckets (adjust as needed)
            num_buckets = 20
            bucket_size = (max_price - min_price) / num_buckets if max_price > min_price else 1

            # 3. prepare buckets as list of dicts
            buckets = [
                {
                    "min": int(min_price + i * bucket_size),
                    "max": int(min_price + (i + 1) * bucket_size),
                    "count": 0
                }
                for i in range(num_buckets)
            ]

            # 4. count cars into buckets
            for car in Car.objects.only("price"):
                if car.price is None:
                    continue
                idx = int((car.price - min_price) / bucket_size)
                if idx == num_buckets:  # edge case for max price
                    idx -= 1
                buckets[idx]["count"] += 1

            # 5. return result
            return {
                "price_range": buckets,
                "min_price": min_price,
                "max_price": max_price,
            }

        return Response({"price": get_price_range()})
