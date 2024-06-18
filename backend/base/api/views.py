from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .serializers import BookSerializer
from rest_framework import status
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