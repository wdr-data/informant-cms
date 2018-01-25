from cms.models import ReportFragment


def augment_fragments(report_id, fragment_id=None):
    from .views.fragments import ReportFragmentSerializer
    serializer = ReportFragmentSerializer(many=True, read_only=True)

    filter = {
        'report': report_id,
    }

    if fragment_id is not None:
        filter['id__gt'] = fragment_id

    fragments = ReportFragment.objects.filter(**filter)
    next_fragments = []

    for fragment in fragments:
        next_fragments.append(fragment)
        if fragment.question:
            break

    return serializer.to_representation(next_fragments)
