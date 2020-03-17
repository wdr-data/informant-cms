from cms.models.subtype import Subtype
from rest_framework import serializers


class SubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtype
        fields = ('emoji', 'title', )
