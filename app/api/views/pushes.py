from cms.models.push import Push
from rest_framework.fields import SerializerMethodField

from .reports import ReportSerializer
from rest_framework import serializers, viewsets


def make_serializer(reqire_published=False):
    class PushSerializer(serializers.ModelSerializer):
        reports = SerializerMethodField()
        last_report = SerializerMethodField()

        def get_reports(self, obj):
            if reqire_published:
                reports_queryset = obj.reports.filter(published=True)
            else:
                reports_queryset = obj.reports.all()

            serializer = ReportSerializer(
                instance=reports_queryset, many=True, read_only=True, context=self.context)
            return serializer.data

        def get_last_report(self, obj):
            if reqire_published:
                last_report = obj.last_report if obj.last_report.published else None
            else:
                last_report = obj.last_report

            if not last_report:
                return None

            serializer = ReportSerializer(
                instance=last_report, many=False, read_only=True, context=self.context)
            return serializer.data

        class Meta:
            model = Push
            fields = (
                'id', 'pub_date', 'timing', 'published', 'delivered_fb', 'delivered_date_fb', 'delivered_tg', 'delivered_date_tg',
                'headline', 'intro', 'reports', 'last_report', 'outro',
                'media', 'media_original', 'media_alt', 'media_note',
            )

    return PushSerializer


PushSerializerPublished = make_serializer(reqire_published=True)
PushSerializerAny = make_serializer(reqire_published=False)


class PushViewSet(viewsets.ModelViewSet):
    filter_fields = ('published', 'delivered_fb', 'delivered_tg', 'pub_date', 'timing')

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return PushSerializerAny
        else:
            return PushSerializerPublished

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Push.objects.order_by('-pub_date')
        else:
            return Push.objects.filter(published=True).order_by('-pub_date')
