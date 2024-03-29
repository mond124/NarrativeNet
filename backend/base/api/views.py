from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions
from fuzzywuzzy import process, fuzz
from plotly import graph_objs as go
from ..models import Book, Genre, Chapter, UserProfile, Author
from .serializers import BookSerializer, ChapterSerializer, UserProfileSerializer
from django.db.models import Q, Count
from django.db import transaction
from django.http import Http404
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.core.cache import cache
import matplotlib.pyplot as plt
import logging

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
    Retrieve books with sorting and filtering including user profile data.
    """
    try:
        sort_by = request.query_params.get('sort_by', 'title')
        genre = request.query_params.get('genre', None)

        # Validate sort_by parameter
        if sort_by not in ['title', 'rating']:
            raise ValidationError("Invalid value for 'sort_by'. It must be either 'title' or 'rating'.")

        # Use caching for frequently accessed data (e.g., all books)
        cache_key = f'books_{sort_by}_{genre}'
        books = cache.get(cache_key)
        if books is None:
            books_query = Book.objects.select_related('author__userprofile')
            if genre:
                books_query = books_query.filter(genres__name__iexact=genre)
            books = books_query.order_by(sort_by)
            cache.set(cache_key, books, timeout=60 * 60)  # Cache for 1 hour

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_books_by_genre(request, genre_name):
    """
    Retrieve books by genre including user profile data, with caching.
    """
    try:
        genres = [genre.strip() for genre in genre_name.split(',')]

        # Validate genre_name parameter with potential caching
        cache_key = f'books_by_genre_{genre_name}'
        valid_genres = cache.get(cache_key)
        if valid_genres is None:
            valid_genres = {genre.name for genre in Genre.objects.all()}
            cache.set(cache_key, valid_genres, timeout=60 * 60 * 24)  # Cache for 1 day

        invalid_genres = [genre for genre in genres if genre not in valid_genres]
        if invalid_genres:
            raise ValidationError(f"Genre(s) '{', '.join(invalid_genres)}' do not exist.")

        # Use caching for frequently accessed genre combinations
        genre_cache_key = f'genre_books_{genre_name}'
        books = cache.get(genre_cache_key)
        if books is None:
            books = Book.objects.select_related('author__userprofile').filter(genres__name__in=genres).distinct()
            cache.set(genre_cache_key, books, timeout=60 * 60)  # Cache for 1 hour (adjust as needed)

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Book.DoesNotExist:
        return Response({"detail": "Books not found for the specified genre(s)."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving books by genre: {e}")
        return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def searchBooks(request):
    """
    Search books by title or synopsis using fuzzy matching.
    """
    try:
        query = request.query_params.get('q', '')
        if not query:
            raise ValidationError("Please provide a search query.")

        # Filter books with case-insensitive search and prefetch related data
        books = Book.objects.select_related('author__userprofile').filter(
            Q(title__icontains=query) | Q(synopsis__icontains=query)
        ).prefetch_related('genres')

        if not books.exists():
            return Response({"detail": "No books found for the search query."}, status=status.HTTP_404_NOT_FOUND)

        titles = [book.title for book in books]
        fuzzy_results = process.extract(query, titles, limit=5)

        fuzzy_matching_results = [
            book for book in books if book.title in [result[0] for result in fuzzy_results] if fuzz.ratio(query.lower(), book.title.lower()) >= 60
        ]
        fuzzy_matching_results.sort(key=lambda x: fuzz.ratio(query.lower(), x.title.lower()), reverse=True)
        serializer = BookSerializer(fuzzy_matching_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkCreateChaptersAPIView(APIView):
    """
    Bulk create chapters with existing chapter title validation.
    """

    def post(self, request, format=None):
        chapters_data = request.data

        # Handle single or list of chapters
        if not isinstance(chapters_data, list):
            chapters_data = [chapters_data]

        existing_chapter_titles = set(Chapter.objects.values_list('title', flat=True))
        new_chapters_data = []
        errors = []

        for chapter_data in chapters_data:
            title = chapter_data.get('title')
            if title in existing_chapter_titles:
                errors.append(f"Chapter '{title}' already exists.")
            else:
                new_chapters_data.append(chapter_data)

        if new_chapters_data:
            serializer = ChapterSerializer(data=new_chapters_data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'chapters': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                errors.extend(serializer.errors)

        if errors:
            return Response({'chapters_errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "No new chapters to create"}, status=status.HTTP_204_NO_CONTENT)

class BulkCreateBooksAndChaptersAPIView(APIView):
    """
    Bulk create books and chapters with validation and potential transaction.
    """

    def post(self, request, format=None):
        books_data = request.data.get('books', [])
        chapters_data = request.data.get('chapters', [])

        response_data = {}

        # Validate and create books in a transaction for data integrity
        with transaction.atomic():
            response_data.update(self._validate_and_create_books(books_data))
            response_data.update(self._validate_and_create_chapters(chapters_data))

        if response_data:
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_NO_CONTENT)

    def _validate_and_create_books(self, books_data):
        """
        Validates and creates books, returning a dictionary with results.
        """
        books_to_create = []
        errors = []
        for book_data in books_data:
            existing_book = Book.objects.filter(title=book_data.get('title')).first()
            if existing_book:
                errors.append(f"Book '{existing_book.title}' already exists.")
            else:
                books_to_create.append(book_data)

        if books_to_create:
            serializer = BookSerializer(data=books_to_create, many=True)
            if serializer.is_valid():
                books = serializer.save()
                for book in books:
                    genres = [Genre.objects.get_or_create(name=genre_name)[0] for genre_name in book_data.get('genres', [])]
                    book.genres.add(*genres)
                response_data = {'books': serializer.data}
            else:
                errors.extend(serializer.errors)

        return {'books_errors': errors} if errors else response_data

    def _validate_and_create_chapters(self, chapters_data):
        """
        Validates and creates chapters, returning a dictionary with results.
        """
        chapters_to_create = []
        errors = []
        for chapter_data in chapters_data:
            existing_chapter = Chapter.objects.filter(title=chapter_data.get('title')).first()
            if existing_chapter:
                errors.append(f"Chapter '{existing_chapter.title}' already exists.")
            else:
                chapters_to_create.append(chapter_data)

        if chapters_to_create:
            serializer = ChapterSerializer(data=chapters_to_create, many=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {'chapters': serializer.data}
            else:
                errors.extend(serializer.errors)

        return {'chapters_errors': errors} if errors else response_data

logger = logging.getLogger(__name__)
@api_view(['POST'])
def createBook(request):
    """
    Create a book or multiple books.

    Handles both single book creation and bulk creation (sending a list of
    book data in the request body).

    Returns detailed success and error information for each book
    in the response data.
    """

    response_data = {"success": [], "error": []}

    for book_data in request.data:
        try:
            author, created = Author.objects.get_or_create(name=book_data['author'])
            serializer = BookSerializer(data=book_data)

            if serializer.is_valid():
                serializer.validated_data['author'] = author
                genres = [
                    Genre.objects.get_or_create(name=genre_name)[0]
                    for genre_name in book_data.get('genres', [])
                ]
                book = serializer.save()
                book.genres.add(*genres)
                response_data["success"].append({
                    "success": "Book created successfully",
                    "book_data": serializer.data
                })
            else:
                response_data["error"].append({
                    "error": str(serializer.errors),
                    "book_data": book_data
                })
        except Exception as e:
            print(f"Error creating book: {e}")
            logger.error(f"Error creating book: {e}")
            response_data["error"].append({
                "error": f"An unexpected error occurred creating book: {e}",
                "book_data": book_data
            })

    if response_data["success"]:
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getGenreDistribution(request):
    """
    Retrieve the distribution of books by genre.
    """
    try:
        genre_counts = Book.objects.values('genres__name').annotate(count=Count('id'))

        genres = [entry['genres__name'] for entry in genre_counts]
        counts = [entry['count'] for entry in genre_counts]

        # Prepare data for Plotly.js
        data_for_plotly = go.Bar(x=genres, y=counts)

        if 'image' in request.query_params:
            # Generate and return the image if requested
            plt.bar(genres, counts)
            plt.xlabel('Genre')
            plt.ylabel('Number of Books')
            plt.title('Distribution of Books by Genre')
            plt.xticks(rotation=45, ha='right')  
            plt.tight_layout()
            plot_path = 'genre_distribution.png'
            plt.savefig(plot_path)  
            plt.close()  

            return Response({'plot_path': plot_path})

        # Return the data suitable for Plotly.js
        return Response({'plot_data': data_for_plotly})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
def getUserProfile(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        raise Http404("User profile does not exist")

@api_view(['PUT'])
def updateUserProfile(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except UserProfile.DoesNotExist:
        raise Http404("User profile does not exist")
    
@api_view(['GET'])
def getChaptersByBook(request, book_id):
    """
    Retrieve chapters by book.
    """
    try:
        chapters = Chapter.objects.filter(book_id=book_id)
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Chapter.DoesNotExist:
        return Response({"detail": "Chapters not found for the specified book."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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