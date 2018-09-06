from cms.models import ReportQuiz

from rest_framework import serializers, viewsets

class ReportQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportQuiz
        fields = ('id', 'correct_option', 'quiz_option', 'quiz_text', 'media_original', 'media',
                  'media_alt', 'media_note', 'report')

class ReportQuizViewSet(viewsets.ModelViewSet):
    queryset = ReportQuiz.objects.all().order_by('id')
    serializer_class = ReportQuizSerializer
    filter_fields = ('report',)
