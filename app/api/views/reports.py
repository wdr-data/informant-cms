from distutils.util import strtobool
from rest_framework import serializers

from cms.models.report import Report, ReportFragment

from .tags import TagSerializer
from .fragments import ModelViewSetWithFragments, ModelSerializerWithFragments, \
    ReportFragmentSerializer
from .genres import GenreSerializer
from .attachments import AttachmentSerializer
from .subtypes import SubtypeSerializer


class ReportSerializer(ModelSerializerWithFragments):
    tags = TagSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    fragment_serializer_class = ReportFragmentSerializer
    attachment = AttachmentSerializer(read_only=True)
    subtype = SubtypeSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    def get_question_count(self, obj):
        return len([frag for frag in obj.fragments.all() if frag.question])

    class Meta:
        model = Report
        fields = (
            'id', 'type', 'subtype', 'created', 'published_date', 'modified', 'is_quiz', 'genres',
            'tags', 'headline', 'summary', 'short_headline', 'audio', 'text', 'attachment',
            'link', 'published', 'delivered_fb', 'delivered_tg', 'author', 'question_count',
        )


class ReportViewSet(ModelViewSetWithFragments):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ReportSerializer
    filter_fields = ('genres', 'tags')

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Report.objects.order_by('-created')
        else:
            return Report.objects.filter(published=True).order_by('-created')
