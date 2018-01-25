from distutils.util import strtobool

from cms.models.report import Report, ReportFragment

from ..utils import augment_fragments
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

    def __init__(self, *args, with_fragments=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.with_fragments = with_fragments

    def to_representation(self, obj):
        rep = super().to_representation(obj)

        if self.with_fragments:
            rep['next_fragments'] = augment_fragments(obj.pk)
        return rep


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Report.objects.all().order_by('-created')
    serializer_class = ReportSerializer
    filter_fields = ('genres', 'topic', 'tags')

    def get_serializer(self, *args, **kwargs):
        kwargs['with_fragments'] = bool(
            strtobool(self.request.query_params.get('withFragments', 'no'))
        )
        return super().get_serializer(*args, **kwargs)
