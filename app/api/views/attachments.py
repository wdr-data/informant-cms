from cms.models.attachment import Attachment
from rest_framework import serializers


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("title", "original", "credit", "processed", "upload_date")
