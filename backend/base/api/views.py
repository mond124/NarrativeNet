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
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity
import matplotlib.pyplot as plt
import math
import logging

logger = logging.getLogger(__name__)

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
        # Get query parameters
        sort_by = request.query_params.get('sort_by', 'title')
        genre = request.query_params.get('genre', None)

        # Validate sort_by parameter
        valid_sort_options = ['title', 'rating']
        if sort_by not in valid_sort_options:
            raise ValidationError(f"Invalid value for 'sort_by'. It must be one of: {', '.join(valid_sort_options)}")

        # Construct cache key
        cache_key = f'books_{sort_by}_{genre}'

        # Check if data is in cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Construct base queryset
        books = Book.objects.select_related('author__userprofile')

        # Apply genre filter if provided
        if genre:
            books = books.filter(genres__name__iexact=genre)

        # Sort queryset based on sort_by parameter
        if sort_by == 'title':
            books = books.order_by('title')
        elif sort_by == 'rating':
            books = books.order_by('-rating')

        # Serialize queryset
        serializer = BookSerializer(books, many=True)
        data = serializer.data

        # Cache the data
        cache.set(cache_key, data, timeout=60 * 60)  # Cache for 1 hour

        # Return response
        return Response(data, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error retrieving books: {e}")
        return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getBooksByGenre(request, genre_name):
    """
    Retrieve books by genre including user profile data, with caching.

    Note: Authentication and permission checks might be required
    in a production environment.
    """

    try:
        genres = [genre.strip() for genre in genre_name.split(',')]

        # Validate genre_name parameter with potential caching
        cache_key = f'books_by_genre_{genre_name}'
        valid_genres = cache.get(cache_key)
        if valid_genres is None:
            valid_genres = {genre.name for genre in Genre.objects.all()}
            cache.set(cache_key, valid_genres)  # Assume reasonable timeout

        invalid_genres = [genre for genre in genres if genre not in valid_genres]
        if invalid_genres:
            raise ValidationError(f"Genre(s) '{', '.join(invalid_genres)}' do not exist.")

        # Construct base queryset (public or filtered by user)
        if request.user.is_authenticated:
            books = Book.objects.select_related('author__userprofile')
        else:
            books = Book.objects.filter(is_public=True).select_related('author__userprofile')

        # Use caching for frequently accessed genre combinations
        genre_cache_key = f'genre_books_{genre_name}'
        books = cache.get(genre_cache_key)
        if books is None:
            books = books.filter(genres__name__in=genres).distinct()
            cache.set(genre_cache_key, books)  # Assume reasonable timeout

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

    Optionally filter by genre and include user profile data.

    Supports pagination using 'page' and 'page_size' query parameters.
    """

    try:
        query = request.query_params.get('query')
        genre = request.query_params.get('genre', None)
        page = int(request.query_params.get('page', 1))  # Default to page 1
        page_size = int(request.query_params.get('page_size', 10))  # Default to 10 results per page

        if query:
            search_vector = SearchVector('title', 'synopsis')
            search_query = SearchQuery(query)

            # Use fuzzy matching (TrigramSimilarity)
            books = books.annotate(similarity=TrigramSimilarity('search_vector', search_query))
            books = books.filter(similarity__gt=0.3).order_by('-similarity')  # Adjust threshold for better results

            # Apply genre filter if provided
            if genre:
                books = books.filter(genres__name__iexact=genre)

            # Implement pagination
            total_results = books.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            books = books[start_index:end_index]

            # Prepare pagination meta data
            pagination_data = {
                'page': page,
                'page_size': page_size,
                'total_pages': math.ceil(total_results / page_size),  # Use math.ceil for accurate page count
                'total_results': total_results,
            }

        else:
            # Handle case where no search query is provided (potentially return empty list)
            books = Book.objects.none()
            pagination_data = {'page': 1, 'page_size': 10, 'total_pages': 0, 'total_results': 0}

        serializer = BookSerializer(books, many=True)
        return Response({'books': serializer.data, 'pagination': pagination_data}, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error searching books: {e}")
        return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        queryset = self.queryset
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def get(self, request, format=None):
        try:
            books = Book.objects.all()
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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