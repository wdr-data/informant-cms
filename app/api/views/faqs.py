from cms.models.faq import FAQ
from .fragments import ModelSerializerWithFragments, FAQFragmentSerializer, \
    ModelViewSetWithFragments


class FAQSerializer(ModelSerializerWithFragments):
    fragment_serializer_class = FAQFragmentSerializer

    class Meta:
        model = FAQ
        fields = ('id', 'name', 'slug', 'text', 'media', 'media_original', 'media_alt', 'media_note')


class FAQViewSet(ModelViewSetWithFragments):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = FAQ.objects.all().order_by('id')
    serializer_class = FAQSerializer
    filter_fields = ('id', 'slug')
