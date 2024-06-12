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

class BookPublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookPublisher
        fields = ['publisher', 'translation', 'edition']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = GenreSerializer()
    bookpublisher = BookPublisherSerializer(many=True)

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'synopsis', 'book_cover', 'rating', 'views', 'bookpublisher']

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')
        bookpublishers_data = validated_data.pop('bookpublisher')

        author, created = Author.objects.get_or_create(name=author_data['name'])
        genre, created = Genre.objects.get_or_create(name=genre_data['name'])
        book = Book.objects.create(author=author, genre=genre, **validated_data)

        for bookpublisher_data in bookpublishers_data:
            publisher_data = bookpublisher_data.pop('publisher')
            publisher, created = Publisher.objects.get_or_create(name=publisher_data['name'])
            BookPublisher.objects.create(book=book, publisher=publisher, **bookpublisher_data)

        return book