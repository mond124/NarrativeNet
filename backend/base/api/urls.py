from django.urls import path
from . import views
from .views import getRoutes
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', getRoutes, name='get_routes'),
]