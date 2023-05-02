"""
test for note APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Note

from note.serializers import (NoteSerializer,
                              NoteDetailSerializer)

NOTES_URL = reverse('note:note-list')


def detail_url(note_id):
    """Create and return a note detail URL."""
    return reverse('note:note-detail', args=[note_id])


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

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test123')
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
        other_user = create_user(email='other@example.com', password='test123')
        create_note(user=other_user)
        create_note(user=self.user)

        res = self.client.get(NOTES_URL)

        notes = Note.objects.filter(user=self.user)
        serializer = NoteSerializer(notes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_note_detail(self):
        """Test get note detail."""
        note = create_note(user=self.user)

        url = detail_url(note.id)
        res = self.client.get(url)

        serializer = NoteDetailSerializer(note)
        self.assertEqual(res.data, serializer.data)

    def test_create_note(self):
        """Test creating a note"""
        payload = {
            'title': 'Sample note',
            'description': 'Something',
        }
        res = self.client.post(NOTES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        note = Note.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(note, key), value)
        self.assertEqual(note.user, self.user)
