from cms.models import FAQFragment
from cms.models import ReportFragment
from cms.models import WikiFragment

from distutils.util import strtobool
from rest_framework import serializers, viewsets


class BaseFragmentViewSet(viewsets.ModelViewSet):
    fragment_group_field = None

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        with_next = strtobool(self.request.query_params.get('withNext', "0"))
        group_field = self.fragment_group_field

        class WithNextSerializer(serializer_class):
            def augment_fragments(self, obj):
                filter = {}
                filter[group_field] = obj[group_field]
                filter['id__gt'] = obj['id']
                fragments = self.Meta.model.objects.filter(**filter)

                next_fragments = []
                for fragment in fragments:
                    next_fragments.append(super().to_representation(fragment))
                    if fragment.question:
                        break

                return next_fragments

            def to_representation(self, obj):
                output = super().to_representation(obj)
                if with_next:
                    output['next_fragments'] = self.augment_fragments(output)
                return output

        kwargs['context'] = self.get_serializer_context()
        return WithNextSerializer(*args, **kwargs)


class ReportFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
                  'link_wiki', 'report')


class ReportFragmentViewSet(BaseFragmentViewSet):
    queryset = ReportFragment.objects.all().order_by('id')
    serializer_class = ReportFragmentSerializer
    filter_fields = ('report',)
    fragment_group_field = 'report'


class FAQFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
                  'link_faq', 'faq')


class FAQFragmentViewSet(BaseFragmentViewSet):
    queryset = FAQFragment.objects.all().order_by('id')
    serializer_class = FAQFragmentSerializer
    filter_fields = ('faq',)
    fragment_group_field = 'faq'


class WikiFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiFragment
        fields = ('id', 'question', 'text', 'media_original', 'media', 'media_note',
                  'link_wiki', 'wiki')


class WikiFragmentViewSet(BaseFragmentViewSet):
    queryset = WikiFragment.objects.all().order_by('id')
    serializer_class = WikiFragmentSerializer
    filter_fields = ('wiki',)
    fragment_group_field = 'wiki'
