from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Book, Chapter
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class TestBookViews(TestCase):
    """
    Test cases for book-related views.
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        cls.access_token = AccessToken.for_user(cls.user)

    def test_get_books_unauthenticated(self):
        """Test retrieving books without authentication."""
        response = self.client.get(reverse('get_books'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_books_authenticated(self):
        """Test retrieving books with authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(reverse('get_books'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions to check the response data


class TestChapterViews(APITestCase):
    """
    Test cases for chapter-related views.
    """

    def test_bulk_create_chapters(self):
        """Test bulk creation of chapters."""
        url = reverse('bulk_create_chapters')
        data = [
            {"title": "Chapter 1", "file": "chapter1.pdf", "book": 1},
            {"title": "Chapter 2", "file": "chapter2.pdf", "book": 1},
            {"title": "Chapter 3", "file": "chapter3.pdf", "book": 2}
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chapter.objects.count(), 3)


class TestBookChapterBulkCreation(APITestCase):
    """
    Test cases for bulk creation of books and chapters.
    """

    def test_bulk_create_books_and_chapters(self):
        """Test bulk creation of books and chapters."""
        url = reverse('bulk_create_books_and_chapters')
        data = {
            "books": [
                {"title": "Book 1", "author": 1, "synopsis": "Synopsis 1", "views": 100, "rating": 4.5},
                {"title": "Book 2", "author": 2, "synopsis": "Synopsis 2", "views": 200, "rating": 4.0}
            ],
            "chapters": [
                {"title": "Chapter 1", "file": "chapter1.pdf", "book": 1},
                {"title": "Chapter 2", "file": "chapter2.pdf", "book": 1},
                {"title": "Chapter 3", "file": "chapter3.pdf", "book": 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Chapter.objects.count(), 3)