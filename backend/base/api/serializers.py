from rest_framework import serializers
from ..models import Book,Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['book_id', 'title', 'synopsis', 'views', 'rating', 'genres']

    def get_genres(self, obj):
        return [genre.name for genre in obj.genres.all()]