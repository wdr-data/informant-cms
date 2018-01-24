from cms.models.report import Report
from rest_framework import serializers, viewsets, routers
from django.conf.urls import url, include


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'created', 'genre', 'topic', 'tags', 
            'headline', 'text', 'published', 'delivered')

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Report.objects.all().order_by('-created')
    serializer_class = ReportSerializer

router = routers.DefaultRouter()
router.register(r'reports', ReportViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # path('report/')
]
