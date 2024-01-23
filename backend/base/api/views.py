from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from ..models import Book
from .serializers import BookSerializer

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
        books = Book.objects.filter(genre=genre_name)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    except Book.DoesNotExist:
        return Response({"detail": "Books not found for the specified genre."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh',
        '/api/data',
    ]
    return Response(routes)