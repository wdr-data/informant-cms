from distutils.util import strtobool

from cms.models.report import Report, ReportFragment

from .tags import TagSerializer
from .fragments import ModelViewSetWithFragments, ModelSerializerWithFragments, \
    ReportFragmentSerializer
from .genres import GenreSerializer


class ReportSerializer(ModelSerializerWithFragments):
    tags = TagSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    fragment_serializer_class = ReportFragmentSerializer

    class Meta:
        model = Report
        fields = ('id', 'type', 'created', 'published_date', 'modified', 'is_quiz', 'genres',
                  'tags', 'headline', 'short_headline', 'audio', 'text',
                  'media', 'media_original', 'media_alt', 'media_note', 'link', 'published', 'delivered', 'author')


class ReportViewSet(ModelViewSetWithFragments):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Report.objects.filter(published=True).order_by('-created')
    serializer_class = ReportSerializer
    filter_fields = ('genres', 'tags')
