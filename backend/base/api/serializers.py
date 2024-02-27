from rest_framework import serializers
from ..models import Book,Genre,Chapter,User, UserProfile

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
    author = serializers.StringRelatedField()
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['book_id', 'title', 'synopsis', 'views', 'rating', 'author', 'genres', 'cover_image_url', 'user_profile']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        else:
            return None
        
    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]
    
    def get_user_profile(self, obj):
        return UserProfileSerializer(obj.author.userprofile).data if obj.author.userprofile else None

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']