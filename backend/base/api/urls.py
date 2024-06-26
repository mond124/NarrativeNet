from django.urls import path
from .views import getRoutes, AddBookView, GetAllBooksView, GetBookView, SearchBookView, BooksByGenreView, GetAllGenresView, GetAllAuthorsView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', getRoutes, name='get_routes'),
    path('add-book/', AddBookView.as_view(), name='add-book'),
    path('books/', GetAllBooksView.as_view(), name='get-all-books'),
    path('books/<int:pk>/', GetBookView.as_view(), name='get-book'),
    path('search/', SearchBookView.as_view(), name='search-books'),
    path('books/genre/<str:genre_name>/', BooksByGenreView.as_view(), name='books-by-genre'),
    path('books/genre/', GetAllGenresView.as_view(), name='get-all-genres'),
    path('books/authors/', GetAllAuthorsView.as_view(), name='get-all-authors'),
]