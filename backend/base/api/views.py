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
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging
from ..models import Author, Genre, Publisher, Book, BookPublisher, Chapter

logger = logging.getLogger(__name__)

class AddBookView(APIView):
    def post(self, request, *args, **kwargs):
        successfully_added = []
        rejected_books = []

        for book_data in request.data:
            serializer = BookSerializer(data=book_data)
            if serializer.is_valid():
                serializer.save()
                successfully_added.append(serializer.data)
            else:
                logger.error(f"Serializer errors: {serializer.errors}")
                rejected_books.append({
                    "data": book_data,
                    "errors": serializer.errors
                })

        if not successfully_added:
            return JsonResponse({
                "status": "error",
                "rejected_books": rejected_books
            }, status=400)

        if rejected_books:
            return JsonResponse({
                "status": "partial_success",
                "successfully_added": successfully_added,
                "rejected_books": rejected_books
            }, status=207)

        return JsonResponse({
            "status": "success",
            "successfully_added": successfully_added
        }, status=201)

class GetAllBooksView(APIView):
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