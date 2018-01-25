from cms.models.report import ReportFragment

from rest_framework import serializers, viewsets


class ReportFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
            'link_wiki', 'report')

class ReportFragmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ReportFragment.objects.all().order_by('id')
    serializer_class = ReportFragmentSerializer
