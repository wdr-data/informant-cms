from cms.models.report import Report
from .tags import TagSerializer
from .genres import GenreSerializer
from .topics import TopicSerializer

from rest_framework import serializers, viewsets, routers
from django.conf.urls import url, include


class ReportSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True, source='genre')
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'created', 'genres', 'topic', 'tags',
            'headline', 'text', 'media', 'media_original', 'media_note', 'published', 'delivered')


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Report.objects.all().order_by('-created')
    serializer_class = ReportSerializer


router = routers.DefaultRouter()
router.register(r'reports', ReportViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # path('report/')
]
