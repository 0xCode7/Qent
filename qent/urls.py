from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from authentication.views import CountriesView, LocationView
from django.conf import settings
from django.conf.urls.static import static

router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),

    path('Downlaod', SpectacularAPIView.as_view(), name='schema'),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('cars.urls')),

    path('api/public/countries/', CountriesView.as_view(), name='countries'),
    path('api/public/register_locations/', LocationView.as_view(), name="location"),

    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)