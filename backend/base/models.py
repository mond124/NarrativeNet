from django.db import models

# Create your models here.
class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    synopsis = models.TextField()
    views = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    genre = models.CharField(max_length=50)

    def __str__(self):
        return self.title