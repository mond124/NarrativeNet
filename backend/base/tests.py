from django.test import TestCase
from rest_framework.test import APIClient
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

