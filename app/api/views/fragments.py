from cms.models import FAQFragment
from cms.models import ReportFragment
from cms.models import WikiFragment

from distutils.util import strtobool
from rest_framework import serializers, viewsets
from .attachments import AttachmentSerializer


class BaseFragmentViewSet(viewsets.ModelViewSet):
    fragment_group_field = None

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        with_next = strtobool(self.request.query_params.get("withNext", "0"))
        group_field = self.fragment_group_field

        class WithNextSerializer(serializer_class):
            def augment_fragments(self, obj):
                filter = {}
                filter[group_field] = obj[group_field]
                filter["id__gt"] = obj["id"]
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
                    output["next_fragments"] = self.augment_fragments(output)
                return output

        kwargs["context"] = self.get_serializer_context()
        return WithNextSerializer(*args, **kwargs)


class ReportFragmentSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = ReportFragment
        fields = ("id", "question", "text", "attachment", "link_wiki", "report")


class ReportFragmentViewSet(BaseFragmentViewSet):
    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return ReportFragment.objects.all().order_by("id")
        else:
            return ReportFragment.objects.filter(report__published=True).order_by("id")

    serializer_class = ReportFragmentSerializer
    filter_fields = ("report",)
    fragment_group_field = "report"


class FAQFragmentSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = FAQFragment
        fields = ("id", "text", "attachment", "faq")


class FAQFragmentViewSet(BaseFragmentViewSet):
    queryset = FAQFragment.objects.all().order_by("id")
    serializer_class = FAQFragmentSerializer
    filter_fields = ("faq",)
    fragment_group_field = "faq"


class WikiFragmentSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = WikiFragment
        fields = ("id", "question", "text", "attachment", "link_wiki", "wiki")


class WikiFragmentViewSet(BaseFragmentViewSet):
    queryset = WikiFragment.objects.all().order_by("id")
    serializer_class = WikiFragmentSerializer
    filter_fields = ("wiki",)
    fragment_group_field = "wiki"


class ModelViewSetWithFragments(viewsets.ModelViewSet):
    def get_serializer(self, *args, **kwargs):
        kwargs["with_fragments"] = bool(
            strtobool(self.request.query_params.get("withFragments", "no"))
        )
        kwargs["all_fragments"] = bool(
            strtobool(self.request.query_params.get("allFragments", "no"))
        )
        return super().get_serializer(*args, **kwargs)


class ModelSerializerWithFragments(serializers.ModelSerializer):
    def __init__(self, *args, with_fragments=False, all_fragments=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.with_fragments = with_fragments
        self.all_fragments = all_fragments

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if not self.with_fragments and not self.all_fragments:
            return rep

        serializer = self.fragment_serializer_class(many=True, read_only=True)
        fragments = obj.fragments.all()

        if self.all_fragments:
            next_fragments = list(fragments)
        else:
            next_fragments = []
            for fragment in fragments:
                next_fragments.append(fragment)
                if fragment.question:
                    break

        rep["next_fragments"] = serializer.to_representation(next_fragments)
        return rep
