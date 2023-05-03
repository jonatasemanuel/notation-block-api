"""
test for note APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Note

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
        """Test creating a note."""
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

    def test_partial_update(self):
        """Test partial update of a note."""
        original_link = 'http://example.com/note.pdf'
        note = create_note(
            user=self.user,
            title='Sample note title',
            ref=original_link,
        )

        payload = {'title': 'New note title'}
        url = detail_url(note.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, payload['title'])
        self.assertEqual(note.ref, original_link)
        self.assertEqual(note.user, self.user)

    def test_full_update(self):
        """Test full update of note"""
        note = create_note(
            user=self.user,
            title='Sample note title',
            ref='http://example.com/note.pdf',
            description='Sample note description.',
            notation='Something'
        )

        payload = {
            'title': 'new note title',
            'ref': 'http://example.com/docs.pdf',
            'description': 'No description.',
            'notation': 'new note',
        }

        url = detail_url(note.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(note, key), value)
        self.assertEqual(note.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the note user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        note = create_note(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(note.id)

        self.client.patch(url, payload)

        note.refresh_from_db()
        self.assertEqual(note.user, self.user)

    def test_delete_note(self):
        """Test deleting a note successful."""
        note = create_note(user=self.user)

        url = detail_url(note.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(id=note.id).exists())

    def test_note_other_users_note_error(self):
        """Test trying to delete another users note give error."""
        new_user = create_user(email='user2@example.com', password='test123')
        note = create_note(user=new_user)

        url = detail_url(note.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=note.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'How ?',
            'res': 'Livro, 2019',
            'description': 'Something....',
            'notation': 'Yes',
            'tags': [{'name': 'Data Science'}, {'name': 'Data Base'}]
        }
        res = self.client.post(NOTES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        notes = Note.objects.filter(user=self.user)
        self.assertEqual(notes.count(), 1)
        note = notes[0]
        self.assertEqual(note.tags.count(), 2)
        for tag in payload['tags']:
            exists = note.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def create_note_with_existing_tags(self):
        """Test creating a note with existing tag."""
        tag_code = Tag.objects.create(user=self.client, name='Code')
        payload = {
            'title': 'Django for begginers',
            'res': 'some like',
            'description': 'Something234....',
            'notation': 'YesYes',
            'tags': [{'name': 'Data Science'}, {'name': 'Code'}]
        }
        res = self.client.post(NOTES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        notes = Note.objects.filter(user=self.user)
        self.assertEqual(notes.count(), 1)
        note = notes[0]
        self.assertEqual(note.tags.count(), 2)
        self.assertIn(tag_code, note.tags.all())
        for tag in payload['tags']:
            exists = note.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a note."""
        note = create_note(user=self.user)

        payload = {'tags': [{'name': 'Nodejs'}]}
        url = detail_url(note.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Nodejs')
        self.assertIn(new_tag, note.tags.all())

    def test_update_note_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_docker = Tag.objects.create(user=self.user, name='Docker')
        note = create_note(user=self.user)
        note.tags.add(tag_docker)

        tag_aws = Tag.objects.create(user=self.user, name='AWS')
        payload = {'tags': [{'name': 'AWS'}]}
        url = detail_url(note.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_aws, note.tags.all())
        self.assertNotIn(tag_docker, note.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a notes tags."""
        tag = Tag.objects.create(user=self.user, name='CSS')
        note = create_note(user=self.user)
        note.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(note.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(note.tags.count(), 0)
