from django.urls import path
from .views import getRoutes, AddBookView, GetAllBooksView, GetBookView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', getRoutes, name='get_routes'),
    path('add-book/', AddBookView.as_view(), name='add-book'),
    path('books/', GetAllBooksView.as_view(), name='get-all-books'),
    path('books/<int:pk>/', GetBookView.as_view(), name='get-book'),
]