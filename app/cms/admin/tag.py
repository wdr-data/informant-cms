import logging

from django.contrib import admin

from ..models.tag import ReportTag
from ..references.dialogflow import delete_entity, EntityType


class ReportTagAdmin(admin.ModelAdmin):

    search_fields = ["name"]
    actions = ["delete_model"]

    class Meta:
        model = ReportTag
        fields = "__all__"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def delete_model(self, request, obj):
        try:
            for o in obj:
                super().delete_model(request, o)

                try:
                    delete_entity(o.name, EntityType.TAGS)
                except Exception as e:
                    logging.error(e)
        except TypeError:
            super().delete_model(request, obj)

            try:
                delete_entity(obj.name, EntityType.TAGS)
            except Exception as e:
                logging.error(e)


# Register your model here
admin.site.register(ReportTag, ReportTagAdmin)
