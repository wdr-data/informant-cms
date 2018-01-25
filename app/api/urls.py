from .views import reports, genres, topics, tags, faqs, pushes, fragments, wikis
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'reports/fragments', fragments.ReportFragmentViewSet)
router.register(r'reports', reports.ReportViewSet)
router.register(r'genres', genres.GenreViewSet)
router.register(r'tags', tags.TagViewSet)
router.register(r'topics', topics.TopicViewSet)
router.register(r'faqs', faqs.FAQViewSet)
router.register(r'pushes', pushes.PushViewSet)
router.register(r'wikis', wikis.WikiViewSet)
