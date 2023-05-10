"""
Views for the note APIs.
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import (mixins,
                            viewsets)
from drf_spectacular.utils import (OpenApiParameter,
                                   OpenApiTypes,
                                   extend_schema,
                                   extend_schema_view)

from note import serializers

from core.models import Note, Tag, Todo, Link


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
        ]
    )
)
class NoteViewSet(viewsets.ModelViewSet):
    """View for manage note APIs."""
    serializer_class = serializers.NoteDetailSerializer
    queryset = Note.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve notes for authenticated user."""
        tags = self.request.query_params.get('tags')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        return queryset.filter(
            user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.NoteSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new note."""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to notes.'
            )
        ]
    )
)
class BaseNoteAttrViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(note__isnull=False)

        return queryset.filter(
            user=self.request.user).order_by('-name').distinct()


class LinkViewSet(BaseNoteAttrViewSet):
    """Manage refs in the database."""
    serializer_class = serializers.LinkSerializer
    queryset = Link.objects.all()


class TagViewSet(BaseNoteAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class TodoViewSet(BaseNoteAttrViewSet):
    """Manage todos in the database."""
    serializer_class = serializers.TodoSerializer
    queryset = Todo.objects.all()

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
