from rest_framework import serializers, viewsets, routers
from django.conf.urls import url, include

from cms.models.faq import FAQ


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ('id', 'name', 'slug', 'text', 'media', 'media_original', 'media_note')


class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = FAQ.objects.all().order_by('id')
    serializer_class = FAQSerializer
    filter_fields = ('id', 'slug')


router = routers.DefaultRouter()
router.register(r'faqs', FAQViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
