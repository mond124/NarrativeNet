from django.contrib import admin
from .models import Author, Genre, Publisher, Book, BookPublisher, Chapter, User, FavoriteBook, FavoriteAuthor, SavedBook, History, UserBehavior
# Register your models here.

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(BookPublisher)
admin.site.register(Chapter)
admin.site.register(User)
admin.site.register(FavoriteBook)
admin.site.register(FavoriteAuthor)
admin.site.register(SavedBook)
admin.site.register(History)
admin.site.register(UserBehavior)