"""
test for note APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Note

from note.serializers import NoteSerializer

NOTES_URL = reverse('note:note-list')


def create_note(user, **params):
    """Create and return a sample note."""
    defaults = {
        'title': 'Sample note title',
        'description': 'Sample description',
        'notation': 'Sample notation',
        'ref': 'http://reference.com/note.pfd',
    }
    defaults.update(params)

    note = Note.objects.create(user=user, **defaults)
    return note


class PublicNoteApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(NOTES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateNoteApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_notes(self):
        """Test retrieving list of notes."""
        create_note(user=self.user)
        create_note(user=self.user)

        res = self.client.get(NOTES_URL)

        notes = Note.objects.all().order_by('-id')
        serializer = NoteSerializer(notes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_note_list_limited_to_user(self):
        """Test list of notes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_note(user=other_user)
        create_note(user=self.user)

        res = self.client.get(NOTES_URL)

        notes = Note.objects.filter(user=self.user)
        serializer = NoteSerializer(notes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
