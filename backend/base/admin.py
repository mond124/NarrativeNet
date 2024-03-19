from django.contrib import admin
from .models import Book, Genre, Chapter, User, UserProfile
# Register your models here.

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Book, Genre, GenreAdmin, Chapter, User, UserProfile)

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'synopsis', 'views', 'rating', 'display_genres')
    filter_horizontal = ('genres',)  # Use filter horizontal widget for genres

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    display_genres.short_description = 'Genres'

admin.site.register(Book, BookAdmin)