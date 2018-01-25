from .views import reports, genres, topics, tags, faqs
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'reports', reports.ReportViewSet)
router.register(r'genres', genres.GenreViewSet)
router.register(r'tags', tags.TagViewSet)
router.register(r'topics', topics.TopicViewSet)
