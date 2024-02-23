from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from fuzzywuzzy import process,fuzz
from ..models import Book, Genre, Chapter
from .serializers import BookSerializer, ChapterSerializer
from django.db.models import Q
from django.db.models import Count
import matplotlib.pyplot as plt

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token obtain pair serializer to include username in the token payload.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view to use the custom serializer.
    """
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def getBooks(request):
    """
    API endpoint to retrieve books with sorting and filtering.
    """
    try:
        sort_by = request.query_params.get('sort_by', 'title')  
        genre = request.query_params.get('genre', None)  

        if genre:
            books = Book.objects.filter(genres__name__iexact=genre)
        else:
            books = Book.objects.all()

        if sort_by == 'title':
            books = books.order_by('title')
        elif sort_by == 'rating':
            books = books.order_by('-rating')  

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getBooksByGenre(request, genre_name):
    """
    API endpoint to retrieve books by genre.
    """
    try:
        genres = [genre.strip() for genre in genre_name.split(',')]
        books = Book.objects.filter(genres__name__in=genres).distinct()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Book.DoesNotExist:
        return Response({"detail": "Books not found for the specified genre(s)."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def searchBooks(request):
    """
    API endpoint to search books by title or synopsis.
    """
    try:
        query = request.query_params.get('q', '')
        if query:
            results = Book.objects.filter(Q(title__icontains=query) | Q(synopsis__icontains=query))
            titles = [book.title for book in results]
            fuzzy_results = process.extract(query, titles, limit=5)

            fuzzy_matching_results = []
            for title, similarity in fuzzy_results:
                if similarity >= 60:
                    book = results.get(title=title)
                    fuzzy_matching_results.append(book)

            fuzzy_matching_results.sort(key=lambda x: fuzz.ratio(query.lower(), x.title.lower()), reverse=True)
            serializer = BookSerializer(fuzzy_matching_results, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Please provide a search query."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkCreateChaptersAPIView(APIView):
    """
    API endpoint to bulk create chapters.
    """
    def post(self, request, format=None):
        try:
            chapters_data = request.data if isinstance(request.data, list) else [request.data]
            response_data = {}
            new_chapters_data = []
            existing_chapter_titles = Chapter.objects.values_list('title', flat=True)
            for chapter_data in chapters_data:
                title = chapter_data.get('title')
                if title not in existing_chapter_titles:
                    new_chapters_data.append(chapter_data)
                else:
                    response_data.setdefault('chapters_errors', []).append(f"Chapter '{title}' already exists.")
            if new_chapters_data:
                chapters_serializer = ChapterSerializer(data=new_chapters_data, many=True)
                if chapters_serializer.is_valid():
                    chapters_serializer.save()
                    response_data['chapters'] = chapters_serializer.data
                else:
                    response_data.setdefault('chapters_errors', []).extend(chapters_serializer.errors)
            else:
                response_data.setdefault('chapters_errors', []).append("No new chapters to create.")
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkCreateBooksAndChaptersAPIView(APIView):
    """
    API endpoint to bulk create books and chapters.
    """
    def post(self, request, format=None):
        try:
            data = request.data
            books_data = data.get('books', [])
            chapters_data = data.get('chapters', [])
            is_single_book = isinstance(books_data, dict)
            is_single_chapter = isinstance(chapters_data, dict)
            response_data = {}
            books_to_create = []
            chapters_to_create = []
            if is_single_book:
                books_data = [books_data]
            if is_single_chapter:
                chapters_data = [chapters_data]
            for book_data in books_data:
                title = book_data.get('title')
                existing_books = Book.objects.filter(title=title)
                if existing_books.exists():
                    response_data.setdefault('books_errors', []).append(f"Book '{title}' already exists.")
                else:
                    books_to_create.append(book_data)
            for chapter_data in chapters_data:
                title = chapter_data.get('title')
                existing_chapters = Chapter.objects.filter(title=title)
                if existing_chapters.exists():
                    response_data.setdefault('chapters_errors', []).append(f"Chapter '{title}' already exists.")
                else:
                    chapters_to_create.append(chapter_data)
            if books_to_create:
                books_serializer = BookSerializer(data=books_to_create, many=True)
                if books_serializer.is_valid():
                    books_serializer.save()
                    response_data['books'] = books_serializer.data
                else:
                    response_data.setdefault('books_errors', []).extend(books_serializer.errors)
            if chapters_to_create:
                chapters_serializer = ChapterSerializer(data=chapters_to_create, many=True)
                if chapters_serializer.is_valid():
                    chapters_serializer.save()
                    response_data['chapters'] = chapters_serializer.data
                else:
                    response_data.setdefault('chapters_errors', []).extend(chapters_serializer.errors)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def createBook(request):
    """
    API endpoint to create a book.
    """
    try:
        if isinstance(request.data, list):
            success_data = []
            error_data = []
            for book_data in request.data:
                serializer = BookSerializer(data=book_data)
                if serializer.is_valid():
                    title = book_data.get('title')
                    existing_books = Book.objects.filter(title__iexact=title)
                    if existing_books.exists():
                        error_data.append({
                            "error": f"Book with title '{title}' already exists.",
                            "book_data": book_data
                        })
                    else:
                        genres_data = book_data.get('genres', [])
                        genres = []
                        for genre_name in genres_data:
                            genre, _ = Genre.objects.get_or_create(name=genre_name)
                            genres.append(genre)
                        book = serializer.save()
                        book.genres.add(*genres)
                        success_data.append({
                            "success": "Book created successfully",
                            "book_data": serializer.data
                        })
                else:
                    error_data.append({
                        "error": serializer.errors,
                        "book_data": book_data
                    })
            response_data = {
                "success": success_data,
                "error": error_data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                title = request.data.get('title')
                existing_books = Book.objects.filter(title__iexact=title)
                if existing_books.exists():
                    return Response({
                        "error": f"Book with title '{title}' already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    genres_data = request.data.get('genres', [])
                    genres = []
                    for genre_name in genres_data:
                        genre, _ = Genre.objects.get_or_create(name=genre_name)
                        genres.append(genre)
                    book = serializer.save()
                    book.genres.add(*genres)
                    return Response({
                        "success": "Book created successfully",
                        "book_data": serializer.data
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getGenreDistribution(request):
    """
    API endpoint to retrieve the distribution of books by genre.
    """
    try:
        genre_counts = Book.objects.values('genres__name').annotate(count=Count('id'))

        genres = [entry['genres__name'] for entry in genre_counts]
        counts = [entry['count'] for entry in genre_counts]

        plt.bar(genres, counts)
        plt.xlabel('Genre')
        plt.ylabel('Number of Books')
        plt.title('Distribution of Books by Genre')
        plt.xticks(rotation=45, ha='right')  

        plt.tight_layout()
        plt.savefig('genre_distribution.png')  
        plt.close()  

        return Response({'message': 'Genre distribution plot generated successfully.', 'plot_path': 'genre_distribution.png'})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def getRoutes(request):
    """
    API endpoint to retrieve available routes.
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