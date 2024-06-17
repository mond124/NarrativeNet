from rest_framework import serializers
from ..models import Author, Genre, Publisher, Book, BookPublisher

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField()
    genre = serializers.CharField()
    publisher = serializers.CharField()
    book_cover = serializers.CharField(required=False)  # Treating book_cover as a path
    translation = serializers.BooleanField(default=False)
    edition = serializers.CharField(default='Original')

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'synopsis', 'publisher', 'translation', 'edition', 'book_cover', 'rating', 'views']

    def create(self, validated_data):
        author_name = validated_data.pop('author')
        genre_name = validated_data.pop('genre')
        publisher_name = validated_data.pop('publisher')

        author, _ = Author.objects.get_or_create(name=author_name)
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

        translation = validated_data.pop('translation', False)
        edition = validated_data.pop('edition', 'Original')

        book = Book.objects.create(
            author=author,
            genre=genre,
            **validated_data
        )

        BookPublisher.objects.create(
            book=book,
            publisher=publisher,
            translation=translation,
            edition=edition
        )

        return book