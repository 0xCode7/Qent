from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


router = routers.SimpleRouter()

urlpatterns = [
    path('api/auth/', include('authentication.urls')),
    path('admin/', admin.site.urls),

    path('Downlaod', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


]
