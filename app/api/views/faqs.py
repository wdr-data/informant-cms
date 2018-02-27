from distutils.util import strtobool
from rest_framework import serializers, viewsets

from cms.models.faq import FAQ, FAQFragment
from .fragments import FAQFragmentSerializer


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ('id', 'name', 'slug', 'text', 'media', 'media_original', 'media_note')

    def __init__(self, *args, with_fragments=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.with_fragments = with_fragments

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if not self.with_fragments:
            return rep

        serializer = FAQFragmentSerializer(many=True, read_only=True)
        fragments = FAQFragment.objects.filter(faq=obj.pk)

        next_fragments = []
        for fragment in fragments:
            next_fragments.append(fragment)
            if fragment.question:
                break

        rep['next_fragments'] = serializer.to_representation(next_fragments)
        return rep


class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = FAQ.objects.all().order_by('id')
    serializer_class = FAQSerializer
    filter_fields = ('id', 'slug', 'name')

    def get_serializer(self, *args, **kwargs):
        kwargs['with_fragments'] = bool(
            strtobool(self.request.query_params.get('withFragments', 'no'))
        )
        return super().get_serializer(*args, **kwargs)