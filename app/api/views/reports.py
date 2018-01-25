from cms.models.report import Report
from .tags import TagSerializer
from .genres import GenreSerializer
from .topics import TopicSerializer

from rest_framework import serializers, viewsets


class ReportSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'created', 'genres', 'topic', 'tags', 'headline', 'text', 'media',
                  'media_original', 'media_note', 'published', 'delivered')


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Report.objects.all().order_by('-created')
    serializer_class = ReportSerializer
