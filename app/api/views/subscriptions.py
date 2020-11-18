from cms.models.subscription import Subscription
from rest_framework import serializers, viewsets


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("psid", "morning", "evening")


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_fields = ("psid", "morning", "evening")
