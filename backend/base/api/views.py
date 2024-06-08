from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from ..models import Author, Genre, Publisher, Book, BookPublisher, Chapter

@method_decorator(csrf_exempt, name='dispatch')
class AddBookView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract data
            title = data.get('title')
            author_name = data.get('author')
            genre_name = data.get('genre')
            synopsis = data.get('synopsis')
            publisher_name = data.get('publisher')
            translation = data.get('translation', False)
            edition = data.get('edition', 'Original')
            book_cover = data.get('book_cover')
            rating = data.get('rating', 0)
            views = data.get('views', 0)

            # Get or create Author
            author, created = Author.objects.get_or_create(name=author_name)

            # Get or create Genre
            genre, created = Genre.objects.get_or_create(name=genre_name)

            # Get or create Publisher
            publisher, created = Publisher.objects.get_or_create(name=publisher_name)

            # Create the Book
            book = Book.objects.create(
                title=title,
                author=author,
                synopsis=synopsis,
                genre=genre,
                book_cover=book_cover,
                rating=rating,
                views=views
            )

            # Create the BookPublisher relation
            BookPublisher.objects.create(
                book=book,
                publisher=publisher,
                translation=translation,
                edition=edition
            )

            return JsonResponse({'status': 'success', 'book_id': book.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
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