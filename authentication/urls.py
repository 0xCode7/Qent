from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('utils/countries/', views.CountriesView.as_view(), name='countries'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),

    path('', include('dj_rest_auth.urls')),  # login, logout, password reset/change

    path('', include('django.contrib.auth.urls')),

]
