from cms.models.topic import Topic
from rest_framework import serializers, generics, urlpatterns
from django.conf.urls import url


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'name')


class TopicView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


urlpatterns = urlpatterns.format_suffix_patterns([
    url(r'topic/(?P<pk>[0-9]+)', TopicView.as_view()),
])
