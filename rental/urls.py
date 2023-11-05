from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('admin',login_required(Admin.as_view()), name='admin'),
    path('biometrics', biometricsAPI, name='biometrics')
]
