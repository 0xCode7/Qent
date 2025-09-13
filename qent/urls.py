from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from authentication.views import CountriesView

router = routers.SimpleRouter()

urlpatterns = [
    path('api/auth/', include('authentication.urls')),

    path('api/public/countries/', CountriesView.as_view(), name='countries'),
    path('admin/', admin.site.urls),

    path('Downlaod', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


]
