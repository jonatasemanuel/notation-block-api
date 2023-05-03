"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Note, Tag


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for notes."""

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'ref', 'created_at',
            'edited_at', 'description', 'notation'
        ]
        read_only_fields = ['id']


class NoteDetailSerializer(NoteSerializer):
    """Serializer for note detail view."""

    class Meta(NoteSerializer.Meta):
        fields = NoteSerializer.Meta.fields + ['description', 'notation']


class TagSerializer(serializers.ModelSerializer):
    """Serializer fot tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
