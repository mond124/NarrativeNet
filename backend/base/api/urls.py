from django.urls import path
from . import views
from .views import MyTokenObtainPairView, getBooks, getBooksByGenre, BulkCreateChaptersAPIView, getRoutes, getGenreDistribution
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('', getRoutes, name='get_routes'),  # Update the path for the getRoutes view
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-profile/<int:user_id>/', views.getUserProfile, name='get_user_profile'),
    path('user-profile/<int:user_id>/update/', views.updateUserProfile, name='update_user_profile'),
    path('books/', getBooks, name='get_books'),
    path('books/<str:genre_name>/', getBooksByGenre, name='get_books_by_genre'),
    path('search-books/', views.searchBooks, name='search_books'),
    path('bulk-create-chapters/', BulkCreateChaptersAPIView.as_view(), name='bulk_create_chapters'),
    path('create-book/', views.createBook, name='create_book'),
    path('bulk-create-books-and-chapters/', views.BulkCreateBooksAndChaptersAPIView.as_view(), name='bulk_create_books_and_chapters'),
    path('genre-distribution/', getGenreDistribution, name='get_genre_distribution'),  # Add path for the getGenreDistribution view
]