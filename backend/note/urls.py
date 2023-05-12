"""
URL mappings for the note app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from note import views

router = DefaultRouter()
router.register('note', views.NoteViewSet)
router.register('tags', views.TagViewSet)
router.register('todos', views.TodoViewSet)
router.register('links', views.LinkViewSet)

app_name = 'note'

urlpatterns = [
    path('', include(router.urls)),
]
