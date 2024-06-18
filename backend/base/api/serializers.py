from rest_framework import serializers
from ..models import Author, Genre, Publisher, Book, BookPublisher, Chapter, User, FavoriteBook, FavoriteAuthor, SavedBook, History, UserBehavior

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class BookPublisherSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()

    class Meta:
        model = BookPublisher
        fields = ['publisher', 'translation', 'edition']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = GenreSerializer()
    publishers = BookPublisherSerializer(source='bookpublisher_set', many=True)
    book_cover = serializers.CharField(required=False)  # Treating book_cover as a path

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'genre', 'synopsis', 'publishers', 'book_cover', 'rating', 'views'
        ]

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')
        publishers_data = validated_data.pop('bookpublisher_set')

        author, _ = Author.objects.get_or_create(name=author_data['name'])
        genre, _ = Genre.objects.get_or_create(name=genre_data['name'])

        book = Book.objects.create(author=author, genre=genre, **validated_data)

        for publisher_data in publishers_data:
            publisher_name = publisher_data.pop('publisher')['name']
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            BookPublisher.objects.create(book=book, publisher=publisher, **publisher_data)

        return book

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'book', 'publisher']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname', 'email']

class FavoriteBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteBook
        fields = ['id', 'user', 'book']

class FavoriteAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteAuthor
        fields = ['id', 'user', 'author']

class SavedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedBook
        fields = ['id', 'user', 'book']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'book', 'last_chapter_read', 'last_read_date']

class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = ['id', 'user', 'book', 'action_type', 'action_date']