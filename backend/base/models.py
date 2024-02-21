from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Check if a genre with the same name exists (case-insensitive)
        existing_genre = Genre.objects.filter(name__iexact=self.name).first()
        if existing_genre and existing_genre != self:
            raise ValidationError({'name': 'Genre with this name already exists.'})

    def save(self, *args, **kwargs):
        # Ensure the name is in title case
        self.name = self.name.title()
        self.full_clean()
        super().save(*args, **kwargs)

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255, default='')  # New field for author
    synopsis = models.TextField()
    views = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    genres = models.ManyToManyField(Genre)
    cover_image = models.ImageField(upload_to='covers/', default='default_cover.jpg')

    def save(self, *args, **kwargs):
        # Normalize title and author to title case before saving
        self.title = self.title.title()
        self.author = self.author.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='chapters/')
    chapter_number = models.IntegerField(null=True, blank=False)

    def save(self, *args, **kwargs):
        # Normalize title to title case before saving
        self.title = self.title.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title}"