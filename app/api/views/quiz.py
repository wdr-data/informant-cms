from rest_framework import serializers, viewsets

from cms.models import ReportQuiz
from .attachments import AttachmentSerializer

class ReportQuizSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = ReportQuiz
        fields = ('id', 'correct_option', 'quiz_option', 'quiz_text', 'attachment', 'report')

class ReportQuizViewSet(viewsets.ModelViewSet):
    queryset = ReportQuiz.objects.all().order_by('id')
    serializer_class = ReportQuizSerializer
    filter_fields = ('report',)
