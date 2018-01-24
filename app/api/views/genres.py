from cms.models.genre import Genre
from rest_framework import serializers, generics, urlpatterns
from django.conf.urls import url


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

class GenreView(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

urlpatterns = urlpatterns.format_suffix_patterns([
    url(r'genre/(?P<pk>[0-9]+)', GenreView.as_view()),
])
