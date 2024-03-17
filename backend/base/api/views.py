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
from django.shortcuts import get_object_or_404
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

        books = Book.objects.select_related('author__userprofile').filter(genres__name__iexact=genre) if genre else Book.objects.select_related('author__userprofile').all()

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
    Retrieve books by genre including user profile data.
    """
    try:
        genres = [genre.strip() for genre in genre_name.split(',')]
        # Validate genre_name parameter
        for genre in genres:
            if not Genre.objects.filter(name__iexact=genre).exists():
                raise ValidationError(f"Genre '{genre}' does not exist.")
        
        books = Book.objects.select_related('author__userprofile').filter(genres__name__in=genres).distinct()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Book.DoesNotExist:
        return Response({"detail": "Books not found for the specified genre(s)."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def searchBooks(request):
    """
    Search books by title or synopsis.
    """
    try:
        query = request.query_params.get('q', '')
        if not query:
            raise ValidationError("Please provide a search query.")

        results = Book.objects.filter(Q(title__icontains=query) | Q(synopsis__icontains=query))
        if not results.exists():
            return Response({"detail": "No books found for the search query."}, status=status.HTTP_404_NOT_FOUND)
        
        titles = [book.title for book in results]
        fuzzy_results = process.extract(query, titles, limit=5)

        fuzzy_matching_results = [results.get(title=title) for title, similarity in fuzzy_results if similarity >= 60]

        fuzzy_matching_results.sort(key=lambda x: fuzz.ratio(query.lower(), x.title.lower()), reverse=True)
        serializer = BookSerializer(fuzzy_matching_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkCreateChaptersAPIView(APIView):
    """
    Bulk create chapters.
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
    Bulk create books and chapters.
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

logger = logging.getLogger(__name__)
@api_view(['POST'])
def createBook(request):
    """
    Create a book or multiple books.

    Handles both single book creation and bulk creation
    (sending a list of book data in the request body).

    Returns detailed success and error information for each book
    in the response data.
    """

    print("Request Data:", request.data)  # Print request data for debugging
    logger.info("Request Data:", request.data)
    if isinstance(request.data, list):  # Handle bulk creation
        success_data = []
        error_data = []
        for book_data in request.data:
            try:
                # Create the author if it doesn't exist
                author, created = Author.objects.get_or_create(name=book_data['author'])

                serializer = BookSerializer(data=book_data)
                if serializer.is_valid():
                    serializer.validated_data['author'] = author  # Set the author object
                    try:
                        book = serializer.save()

                        # Save the book before adding genres
                        serializer.save_m2m()

                        # Associate genres
                        book.genres.add(*book_data.get('genres', []))

                        success_data.append({
                            "success": "Book created successfully",
                            "book_data": serializer.data
                        })
                    except ValidationError as e:
                        # Log specific validation errors
                        print(f"Validation error creating book ({book_data}): {e}")
                        logger.error(f"Validation error creating book ({book_data}): {e}")
                        error_data.append({
                            "error": str(e),  # Get detailed error message
                            "book_data": book_data
                        })
                else:
                    error_data.append({
                        "error": serializer.errors,  # Use serializer errors for detailed messages
                        "book_data": book_data
                    })

            except Exception as e:
                # Handle other errors during book creation
                print(f"Error creating book: {e}")
                logger.error(f"Error creating book: {e}")
                error_data.append({
                    "error": f"An unexpected error occurred creating book: {e}",
                    "book_data": book_data
                })

        response_data = {
            "success": success_data,
            "error": error_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    else:  # Handle single book creation
        try:
            # Create the author if it doesn't exist
            author, created = Author.objects.get_or_create(name=request.data['author'])

            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['author'] = author  # Set the author object
                try:
                    book = serializer.save()

                    # Save the book before adding genres
                    serializer.save_m2m()

                    # Associate genres
                    book.genres.add(*request.data.get('genres', []))

                    return Response({
                        "success": "Book created successfully",
                        "book_data": serializer.data
                    }, status=status.HTTP_201_CREATED)
                except ValidationError as e:
                    # Log specific validation errors
                    print(f"Validation error creating book: {e}")
                    logger.error(f"Validation error creating book: {e}")
                    return Response({
                        "error": str(e),  # Get detailed error message
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                print("Serializer Errors:", serializer.errors)  # Print serializer errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle other errors during book creation
            print(f"Error creating book: {e}")
            logger.error(f"Error creating book: {e}")
            return Response({"detail": "An unexpected error occurred while creating book(s)."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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