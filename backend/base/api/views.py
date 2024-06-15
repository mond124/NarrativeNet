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
        try:
            # Determine if the request contains multiple books
            is_many = isinstance(request.data, list)
            serializer = BookSerializer(data=request.data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'status': 'success'}, status=201)
            else:
                logger.error(f"Serializer errors: {serializer.errors}")
                # Structure the response to include the invalid data and errors
                if is_many:
                    rejected_books = [
                        {'data': data, 'errors': error}
                        for data, error in zip(request.data, serializer.errors)
                    ]
                else:
                    rejected_books = {'data': request.data, 'errors': serializer.errors}

                return JsonResponse({'status': 'error', 'rejected_books': rejected_books}, status=400, safe=False)
        except KeyError as e:
            return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

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