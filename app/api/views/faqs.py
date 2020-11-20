from cms.models.faq import FAQ
from .fragments import (
    ModelSerializerWithFragments,
    FAQFragmentSerializer,
    ModelViewSetWithFragments,
)
from .attachments import AttachmentSerializer


class FAQSerializer(ModelSerializerWithFragments):
    fragment_serializer_class = FAQFragmentSerializer
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = FAQ
        fields = ("id", "name", "slug", "text", "attachment")


class FAQViewSet(ModelViewSetWithFragments):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = FAQ.objects.all().order_by("id")
    serializer_class = FAQSerializer
    filter_fields = ("id", "slug")
