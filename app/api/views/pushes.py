from cms.models.push import Push
from rest_framework.fields import SerializerMethodField

from .reports import ReportSerializer
from rest_framework import serializers, viewsets


class PushSerializer(serializers.ModelSerializer):
    reports = SerializerMethodField()

    def get_reports(self, obj):
        reports_queryset = obj.reports.filter(published=True)
        serializer = ReportSerializer(
            instance=reports_queryset, many=True, read_only=True, context=self.context)
        return serializer.data

    class Meta:
        model = Push
        fields = (
            'id', 'pub_date', 'timing', 'published', 'delivered', 'delivered_date',
            'headline', 'intro', 'reports', 'outro',
            'media', 'media_original', 'media_alt', 'media_note',
        )


class PushViewSet(viewsets.ModelViewSet):
    serializer_class = PushSerializer
    filter_fields = ('published', 'delivered', 'pub_date', 'timing')

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Push.objects.order_by('-pub_date', '-delivered_date')
        else:
            return Push.objects.filter(published=True).order_by('-pub_date', '-delivered_date')
