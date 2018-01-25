from cms.models.report import ReportTag
from rest_framework import serializers, generics, urlpatterns
from django.conf.urls import url


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTag
        fields = ('id', 'name')


class TagView(generics.RetrieveAPIView):
    queryset = ReportTag.objects.all()
    serializer_class = TagSerializer


urlpatterns = urlpatterns.format_suffix_patterns([
    url(r'tag/(?P<pk>[0-9]+)', TagView.as_view()),
])
