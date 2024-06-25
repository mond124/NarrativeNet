from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .serializers import BookSerializer, GenreSerializer, AuthorSerializer
from rest_framework import status
from fuzzywuzzy import fuzz
from django.db.models.functions import Length
import logging
from ..models import Author, Genre, Publisher, Book, BookPublisher, Chapter

logger = logging.getLogger(__name__)

class AddBookView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BookSerializer(data=request.data, many=isinstance(request.data, list))
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'accepted_books': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({'status': 'error', 'rejected_books': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GetAllBooksView(APIView):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().values(
            'id', 'title', 'synopsis', 'book_cover', 'rating', 'views', 'author__name', 'genre__name'
        )
        return JsonResponse(list(books), safe=False)
    
class GetBookView(APIView):
    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SearchBookView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        threshold = 60
        books = Book.objects.annotate(title_length=Length('title')).order_by('title_length')[:100]
        matching_books = []

        for book in books:
            similarity = fuzz.token_set_ratio(query, book.title)
            if similarity >= threshold:
                serializer = BookSerializer(book)
                matching_books.append({'book': serializer.data, 'similarity': similarity})

        if not matching_books:
            return Response({'message': 'No matching books found'}, status=status.HTTP_404_NOT_FOUND)

        matching_books = sorted(matching_books, key=lambda x: x['similarity'], reverse=True)

        return Response({'results': matching_books}, status=status.HTTP_200_OK)

class BooksByGenreView(APIView):
    def get(self, request, genre_name, *args, **kwargs):
        genre = get_object_or_404(Genre, name=genre_name)
        books = Book.objects.filter(genre=genre)
        if not books.exists():
            return Response({'message': f'No books found for genre: {genre_name}'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(books, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)
            
class GetAllGenresView(APIView):
    def get(self, request, *args, **kwargs):
        genres = Genre.objects.all()
        if not genres.exists():
            return Response({'message': 'No genres found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GenreSerializer(genres, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)

class GetAllAuthorsView(APIView):
    def get(self, request, *args, **kwargs):
        authors = Author.objects.all()
        if not authors.exists():
            return Response({'message': 'No authors found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AuthorSerializer(authors, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def getRoutes(request):
    """
    Retrieve available routes.
    """
    routes = [
        '/api/token',
        '/api/token/refresh',
        '/api/books',
        '/api/books/<str:genre_name>/',
        '/api/data',
        '/api/search-books/?query=<search_query>',
    ]
    return Response(routes)