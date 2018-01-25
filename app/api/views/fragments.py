from cms.models.report import ReportFragment

from rest_framework import serializers, viewsets


class ReportFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
            'link_wiki', 'report')

    def to_representation(self, obj):
        output = super().to_representation(obj)
        fragments = ReportFragment.objects.filter(report=obj.report, id__gt=obj.id)
        fragment_out = [super(ReportFragmentSerializer, self).to_representation(fragment) for fragment in fragments]
        output['next_fragments'] = fragment_out
        return output

class ReportFragmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ReportFragment.objects.all().order_by('id')
    serializer_class = ReportFragmentSerializer
    filter_fields = ('report', )
