from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from fuzzywuzzy import process,fuzz
from ..models import Book, Genre
from .serializers import BookSerializer, ChapterSerializer
from django.db.models import Q

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def getBooks(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getBooksByGenre(request, genre_name):
    try:
        genres = [genre.strip() for genre in genre_name.split(',')]
        books = Book.objects.filter(genres__name__in=genres).distinct()        
        print(f"Books for genre(s) '{', '.join(genres)}': {books}")  # Debug print
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Book.DoesNotExist:
        return Response({"detail": "Books not found for the specified genre(s)."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def searchBooks(request):
    query = request.query_params.get('q', '')
    if query:
        # Perform a case-insensitive search across title and synopsis fields
        results = Book.objects.filter(Q(title__icontains=query) | Q(synopsis__icontains=query))

        # Fuzzy matching for handling typos
        titles = [book.title for book in results]
        fuzzy_results = process.extract(query, titles, limit=5)

        # Filter books based on fuzzy matched titles and similarity threshold
        fuzzy_matching_results = []
        for title, similarity in fuzzy_results:
            if similarity >= 60:  # Adjust the threshold as needed
                book = results.get(title=title)
                fuzzy_matching_results.append(book)

        # Sort the results by similarity
        fuzzy_matching_results.sort(key=lambda x: fuzz.ratio(query.lower(), x.title.lower()), reverse=True)

        serializer = BookSerializer(fuzzy_matching_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Please provide a search query."}, status=status.HTTP_400_BAD_REQUEST)

class BulkCreateChaptersAPIView(APIView):
    def post(self, request, format=None):
        chapters_data = request.data  # Assuming the JSON data is sent as the request body
        chapters_serializer = ChapterSerializer(data=chapters_data, many=True)
        if chapters_serializer.is_valid():
            chapters_serializer.save()  # Save the chapters to the database
            return Response(chapters_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(chapters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BulkCreateBooksAndChaptersAPIView(APIView):
    def post(self, request, format=None):
        data = request.data
        books_data = data.get('books', [])
        chapters_data = data.get('chapters', [])

        books_serializer = BookSerializer(data=books_data, many=True)
        chapters_serializer = ChapterSerializer(data=chapters_data, many=True)

        response_data = {}
        if books_serializer.is_valid():
            books_serializer.save()
            response_data['books'] = books_serializer.data
        else:
            response_data['books_errors'] = books_serializer.errors

        if chapters_serializer.is_valid():
            chapters_serializer.save()
            response_data['chapters'] = chapters_serializer.data
        else:
            response_data['chapters_errors'] = chapters_serializer.errors

        return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def createBook(request):
    if isinstance(request.data, list):  # Check if data is a list (bulk creation)
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
    else:  # Single book creation
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh',
        '/api/books',
        '/api/books/<str:genre_name>/',
        '/api/data',
        '/api/search-books/?query=<search_query>',
    ]
    return Response(routes)