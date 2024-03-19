from django.contrib import admin
from .models import Book, Genre, Chapter, UserProfile, Author
# Register your models here.

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Genre, GenreAdmin)
admin.site.register(Chapter)
admin.site.register(UserProfile)
admin.site.register(Author)

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'synopsis', 'views', 'rating', 'display_genres')
    filter_horizontal = ('genres',)  # Use filter horizontal widget for genres

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    display_genres.short_description = 'Genres'

admin.site.register(Book, BookAdmin)