from cms.models.push import Push
from .reports import ReportSerializer
from rest_framework import serializers, viewsets

class PushSerializer(serializers.ModelSerializer):
  reports = ReportSerializer(many=True, read_only=True)
  class Meta:
    model = Push
    fields = ('id', 'pub_date', 'published', 'delivered',
              'breaking', 'headline', 'intro', 'reports', 'outro'
             )

class PushViewSet(viewsets.ModelViewSet):
  queryset = Push.objects.all().order_by('-pub_date')
  serializer_class = PushSerializer
  filter_fields = ('published', 'delivered', 'breaking')
 