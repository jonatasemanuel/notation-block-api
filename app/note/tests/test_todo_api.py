"""
Tests for the todo API.
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from note.serializers import TodoSerializer
from core.models import Todo

TODOS_URL = reverse('note:todo-list')


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(
                                                email=email,
                                                password=password)


class PublicTodosApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieve"""
        res = self.client.get(TODOS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTodosApiTests(TestCase):
    """Test anauthenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_todos(self):
        """Test retrieving a list of todos"""
        Todo.objects.create(user=self.user, title='Write 5 lines of...')
        Todo.objects.create(user=self.user, title='Refactor the code')

        res = self.client.get(TODOS_URL)

        todos = Todo.objects.all().order_by('-id')
        serializer = TodoSerializer(todos, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_todos_limited_to_user(self):
        """Test list of todos is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Todo.objects.create(user=user2, title='Clean setup')
        todo = Todo.objects.create(user=self.user, title='Read a book')

        res = self.client.get(TODOS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], todo.title)
        self.assertEqual(res.data[0]['id'], todo.id)
