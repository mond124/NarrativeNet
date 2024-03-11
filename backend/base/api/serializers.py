from rest_framework import serializers
from ..models import Book, Genre, Chapter, User, UserProfile, Author

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'file']

class BookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['book_id', 'title', 'synopsis', 'views', 'rating', 'author', 'genres', 'cover_image_url', 'user_profile']

    def get_author_name(self, obj):
        return obj.author.name if obj.author else None

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        else:
            return None
        
    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]
    
    def get_user_profile(self, obj):
        return UserProfileSerializer(obj.author.userprofile).data if obj.author.userprofile else None

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class UserProfileSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True)
    favorite_authors = serializers.SerializerMethodField()
    favorite_books = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user', 'favorite_genres', 'favorite_authors', 'favorite_books']

    def get_favorite_authors(self, obj):
        return AuthorSerializer(obj.favorite_authors.all(), many=True).data

    def get_favorite_books(self, obj):
        return BookSerializer(obj.favorite_books.all(), many=True).data
    
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']