from rest_framework import serializers
from ..models import Book,Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    text_path = serializers.CharField(source='text_path.url')
    image_path = serializers.CharField(source='image_path.url')

    class Meta:
        model = Book
        fields = ['book_id', 'title', 'synopsis', 'views', 'rating', 'genres', 'text_path', 'image_path']

    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]