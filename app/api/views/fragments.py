from ..utils import augment_fragments

from cms.models.report import ReportFragment

from distutils.util import strtobool
from rest_framework import serializers, viewsets


class BaseFragmentViewSet(viewsets.ModelViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        with_next = strtobool(self.request.query_params.get('withNext', "0"))

        class WithNextSerializer(serializer_class):
            def to_representation(self, obj):
                output = super().to_representation(obj)
                if with_next:
                    output['next_fragments'] = augment_fragments(obj.report, obj.id)
                return output

        kwargs['context'] = self.get_serializer_context()
        return WithNextSerializer(*args, **kwargs)


class ReportFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
                  'link_wiki', 'report')


class ReportFragmentViewSet(BaseFragmentViewSet):
    queryset = ReportFragment.objects.all().order_by('id')
    serializer_class = ReportFragmentSerializer
    filter_fields = ('report',)
