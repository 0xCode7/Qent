from django.urls import path
from .views import CarListView, CarDetailView, ReviewCreateView, BrandListView, BestCarsListView, NearestCarListView, \
    BrandDetailsView, CarSearchView, GetAllReviewsView, SubscribeCarView

urlpatterns = [
    path("cars/", CarListView.as_view(), name="car_list"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:car_id>/reviews", GetAllReviewsView.as_view(), name="get_car_review"),
    path("cars/<int:car_id>/reviews/add", ReviewCreateView.as_view(), name="add_car_review"),
    path("cars/<int:pk>/subscribe/", SubscribeCarView.as_view(), name="car-subscribe"),
    path("cars/best", BestCarsListView.as_view(), name="best_cars"),
    path("cars/nearest", NearestCarListView.as_view(), name="nearest_cars"),
    path("brands/", BrandListView.as_view(), name="brand_list"),
    path("brands/<int:pk>", BrandDetailsView.as_view(), name="brand_list"),
    path("cars/search/", CarSearchView.as_view(), name="search"),

]
