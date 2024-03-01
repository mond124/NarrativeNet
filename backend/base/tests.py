from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Book, Genre, Chapter, Author
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class TestBookViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.access_token = AccessToken.for_user(self.user)
        
    def test_get_books(self):
        # Test retrieving books without authentication
        response = self.client.get(reverse('get_books'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test retrieving books with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(reverse('get_books'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions to check the response data
    
    def test_get_books_by_genre(self):
        # Test retrieving books by genre without authentication
        response = self.client.get(reverse('get_books_by_genre', kwargs={'genre_name': 'fantasy'}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test retrieving books by genre with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(reverse('get_books_by_genre', kwargs={'genre_name': 'fantasy'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions to check the response data
    
    def test_search_books(self):
        # Test searching books without authentication
        response = self.client.get(reverse('search_books') + '?q=fantasy')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test searching books with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(reverse('search_books') + '?q=fantasy')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions to check the response data
    
    def test_create_book(self):
        # Test creating a book without authentication
        data = {'title': 'Test Book', 'author': 'Test Author', 'synopsis': 'Test Synopsis', 'views': 0, 'rating': 0}
        response = self.client.post(reverse('create_book'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test creating a book with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(reverse('create_book'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Add more assertions to check the response data

class TestBulkCreateChaptersAPIView(APITestCase):
    def test_bulk_create_chapters(self):
        url = reverse('bulk_create_chapters')
        data = [
            {"title": "Chapter 1", "file": "chapter1.pdf", "book": 1},
            {"title": "Chapter 2", "file": "chapter2.pdf", "book": 1},
            {"title": "Chapter 3", "file": "chapter3.pdf", "book": 2}
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chapter.objects.count(), 3)

class TestBulkCreateBooksAndChaptersAPIView(APITestCase):
    def test_bulk_create_books_and_chapters(self):
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

class TestGetGenreDistribution(APITestCase):
    def test_get_genre_distribution(self):
        url = reverse('get_genre_distribution')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions based on expected response data

class TestGetRoutes(APITestCase):
    def test_get_routes(self):
        url = reverse('get_routes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions based on expected response data