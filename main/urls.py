from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from .views import HealthCheck
from user.urls import urlpatterns as user_urls
from rental.urls import urlpatterns as rental_urls

urlpatterns = [
    path("admin-django/", admin.site.urls),
    path("health-check/", HealthCheck.as_view(), name="health-check"),
    # JWT Token Authentication
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    # Swagger
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    # User
    path("users/", include(user_urls)),
    # Rental
    path("rental/", include(rental_urls)),
]
