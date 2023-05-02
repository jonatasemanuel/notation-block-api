"""
URL mappings for the note app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from note import views

router = DefaultRouter()
router.register('note', views.NoteViewSet)

app_name = 'note'

urlpatterns = [
    path('', include(router.urls)),
]
