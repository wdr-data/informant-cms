from .views import reports, genres, topics, tags, faqs
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'reports', reports.ReportViewSet)

urlpatterns = []
urlpatterns += [url(r'^', include(router.urls))]
urlpatterns += genres.urlpatterns
urlpatterns += topics.urlpatterns
urlpatterns += tags.urlpatterns
urlpatterns += faqs.urlpatterns
