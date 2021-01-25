from cms.models.push_compact import PushCompact, Teaser, Promo
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers, viewsets

from .attachments import AttachmentSerializer


class TeaserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teaser
        fields = (
            "headline",
            "summary",
            "short_headline",
            "link",
        )


class PromoSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = Promo
        fields = (
            "attachment",
            "text",
            "link_name",
            "link",
        )


class PushCompactSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)
    teasers = TeaserSerializer(many=True, read_only=True)
    promo = PromoSerializer(read_only=True)
    timing = SerializerMethodField()

    def get_timing(self, obj):
        return "morning"

    class Meta:
        model = PushCompact
        fields = (
            "id",
            "pub_date",
            "published",
            "timing",
            "delivered_fb",
            "delivered_date_fb",
            "delivered_tg",
            "delivered_date_tg",
            "attachment",
            "intro",
            "teasers",
            "outro",
            "promo",
        )


class PushCompactViewSet(viewsets.ModelViewSet):
    filter_fields = ("published", "delivered_fb", "delivered_tg", "pub_date")
    serializer_class = PushCompactSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return PushCompact.objects.order_by("-pub_date", "-delivered_date_fb")
        else:
            return PushCompact.objects.filter(published=True).order_by(
                "-pub_date", "-delivered_date_fb"
            )
