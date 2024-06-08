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
    
class BookPublisher(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    translation = models.BooleanField(default=False)
    edition = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.book.title} - {self.publisher.name} ({'Translation' if self.translation else 'Original'})"
    
class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title
    
class User(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
class FavoriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.book.title}"

class FavoriteAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.author.name}"

class SavedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.book.title}"
    
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    last_chapter_read = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    last_read_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.book.title} (Last read: {self.last_read_date})"

class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.book.title} ({self.action_type})"