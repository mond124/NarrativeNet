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
    text_path = models.FileField(upload_to='texts/', default='default_text.txt')
    image_path = models.ImageField(upload_to='images/', default='default_image.jpg')

    def __str__(self):
        return self.title