from .views import reports, genres, tags, faqs, pushes, fragments, wikis, subscriptions, quiz
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'reports/fragments', fragments.ReportFragmentViewSet, basename='report fragment')
router.register(r'quiz', quiz.ReportQuizViewSet)
router.register(r'reports', reports.ReportViewSet, basename='reports')
router.register(r'genres', genres.GenreViewSet)
router.register(r'tags', tags.TagViewSet)
router.register(r'faqs/fragments', fragments.FAQFragmentViewSet)
router.register(r'faqs', faqs.FAQViewSet)
router.register(r'pushes', pushes.PushViewSet, basename='pushes')
router.register(r'wikis/fragments', fragments.WikiFragmentViewSet)
router.register(r'wikis', wikis.WikiViewSet)
router.register(r'subscriptions', subscriptions.SubscriptionViewSet)
