from rest_framework import serializers
from ..models import Book,Genre,Chapter

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

    class Meta:
        model = Book
        fields = ['book_id', 'title', 'synopsis', 'views', 'rating', 'author', 'genres', 'cover_image_url']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        else:
            return None
        
    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]