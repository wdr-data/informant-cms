from rest_framework import serializers, viewsets

from cms.models.wiki import Wiki
from .tags import TagSerializer
from .genres import GenreSerializer
from .attachments import AttachmentSerializer


class WikiSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = Wiki
        fields = ("id", "name", "follow_up_at", "genres", "tags", "text", "attachment")


class WikiViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Wiki.objects.all().order_by("id")
    serializer_class = WikiSerializer
    filter_fields = ("id", "name", "follow_up_at", "genres", "tags")
