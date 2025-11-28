from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from authentication.views import CountriesView, LocationView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

from cars.views import APISettings

router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),

    path('Downlaod', SpectacularAPIView.as_view(), name='schema'),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('cars.urls')),

    path('api/public/countries/', CountriesView.as_view(), name='countries'),
    path('api/public/settings/', APISettings.as_view(), name='settings'),
    path('api/public/register_locations/', LocationView.as_view(), name="location"),

    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


]


# Serve static & media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
