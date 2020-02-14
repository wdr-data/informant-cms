from cms.models.push import Push
from rest_framework.fields import SerializerMethodField

from .reports import ReportSerializer
from rest_framework import serializers, viewsets


def make_serializer(reqire_published=False):
    class PushSerializer(serializers.ModelSerializer):
        reports = SerializerMethodField()

        def get_reports(self, obj):
            if reqire_published:
                reports_queryset = obj.reports.filter(published=True)
                last_report = obj.last_report if obj.last_report and obj.last_report.published else None
            else:
                reports_queryset = obj.reports.all()
                last_report = obj.last_report

            reports = list(reports_queryset)

            if last_report:
                reports.append(last_report)

            serializer = ReportSerializer(
                instance=reports, many=True, read_only=True, context=self.context)
            return serializer.data

        class Meta:
            model = Push
            fields = (
                'id', 'pub_date', 'timing', 'published', 'delivered_fb', 'delivered_date_fb', 'delivered_tg', 'delivered_date_tg',
                'headline', 'intro', 'reports', 'outro',
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
