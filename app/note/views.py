"""
Views for the note APIs.
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from note import serializers

from core.models import Note


class NoteViewSet(viewsets.ModelViewSet):
    """View for manage note APIs."""
    serializer_class = serializers.NoteSerializer
    queryset = Note.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve notes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
