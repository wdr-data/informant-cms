from ..utils import augment_fragments

from cms.models.report import ReportFragment

from distutils.util import strtobool
from rest_framework import serializers, viewsets


class ReportFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
            'link_wiki', 'report')

    def __init__(self, *args, with_next=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._with_next = with_next

    def to_representation(self, obj):
        output = super().to_representation(obj)
        if self._with_next:
            output['next_fragments'] = augment_fragments(obj.report, obj.id)
        return output


class ReportFragmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ReportFragment.objects.all().order_by('id')
    serializer_class = ReportFragmentSerializer
    filter_fields = ('report', )

    def get_serializer(self, *args, **kwargs):
        kwargs['with_next'] = strtobool(self.request.query_params.get('withNext', "0"))
        return super().get_serializer(*args, **kwargs)
