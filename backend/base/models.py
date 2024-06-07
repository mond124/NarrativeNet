from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    synopsis = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    book_cover = models.ImageField(upload_to='book_covers/')
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    views = models.IntegerField()

    def __str__(self):
        return self.title