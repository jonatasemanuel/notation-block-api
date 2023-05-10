"""
Tests for the tags API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from note.serializers import LinkSerializer
from core.models import Link

LINKS_URL = reverse('note:link-list')


def detail_url(link_id):
    """Create and return a link detail url."""
    return reverse('note:link-detail', args=[link_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class PublicLinksApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving refs."""
        res = self.client.get(LINKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLinksApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_links(self):
        """Test retrieving a list of refs."""
        Link.objects.create(user=self.user, name='https://some.link')
        Link.objects.create(user=self.user, name='Rincon Sapiência')

        res = self.client.get(LINKS_URL)

        links = Link.objects.all().order_by('-name')
        serializer = LinkSerializer(links, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_links_limited_to_user(self):
        """Test list of refs is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Link.objects.create(user=user2, name='Uncle Bob, 2019')
        link = Link.objects.create(
            user=self.user,
            name='https://example.exp.org'
        )

        res = self.client.get(LINKS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], link.name)
        self.assertEqual(res.data[0]['id'], link.id)

    def test_update_link(self):
        """Test updating a link."""
        link = Link.objects.create(user=self.user, name='Bob, 2019')

        payload = {'name': 'doc.com'}
        url = detail_url(link.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        link.refresh_from_db()
        self.assertEqual(link.name, payload['name'])

    def test_delete_link(self):
        """Test deleting a link."""
        link = Link.objects.create(user=self.user, name='https://some.com')

        url = detail_url(link.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        links = Link.objects.filter(user=self.user)
        self.assertFalse(links.exists())
