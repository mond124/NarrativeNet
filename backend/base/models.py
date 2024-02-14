from django.db import models

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    synopsis = models.TextField()
    views = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    genres = models.ManyToManyField(Genre)
    cover_image = models.ImageField(upload_to='covers/', default='default_cover.jpg')

    def __str__(self):
        return self.title

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='chapters/')

    def __str__(self):
        return f"{self.book.title} - {self.title}"