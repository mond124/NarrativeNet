from django.urls import path
from .views import getRoutes, AddBookView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', getRoutes, name='get_routes'),
    path('add-book/', AddBookView.as_view(), name='add-book'),
]