from cms.models.tag import ReportTag
from rest_framework import serializers, viewsets


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTag
        fields = ("id", "name")


class TagViewSet(viewsets.ModelViewSet):
    queryset = ReportTag.objects.all()
    serializer_class = TagSerializer
    filter_fields = ("name",)
