"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer fot tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for notes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'ref', 'created_at',
            'edited_at', 'description', 'notation', 'tags'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, note):
        """Handle gettin or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            note.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a note."""
        tags = validated_data.pop('tags', [])
        note = Note.objects.create(**validated_data)
        self._get_or_create_tags(tags, note)

        return note

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class NoteDetailSerializer(NoteSerializer):
    """Serializer for note detail view."""

    class Meta(NoteSerializer.Meta):
        fields = NoteSerializer.Meta.fields + ['description', 'notation']
