from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .serializers import BookSerializer
from rest_framework import status
import json
from ..models import Author, Genre, Publisher, Book, BookPublisher, Chapter


class AddBookView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BookSerializer(data=request.data, many=isinstance(request.data, list))
        if serializer.is_valid():
            serializer.save()
            book_ids = [book.id for book in serializer.instance] if isinstance(serializer.instance, list) else [serializer.instance.id]
            return Response({'status': 'success', 'book_ids': book_ids}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class GetAllBooksView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().values(
            'id', 'title', 'synopsis', 'book_cover', 'rating', 'views', 'author__name', 'genre__name'
        )
        return JsonResponse(list(books), safe=False)
        
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