from django.contrib import admin

from ..models.topic import Topic
from ..references.dialogflow import add_entry, delete_entry, Entity


class TopicAdmin(admin.ModelAdmin):
    actions = ['delete_model']

    class Meta:
        model = Topic
        fields = "__all__"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        add_entry(obj.name, Entity.TOPICS, optional=True)

    def delete_model(self, request, obj):
        try:
            for o in obj:
                super().delete_model(request, o)

                delete_entry(o.name, Entity.TOPICS, optional=True)
        except TypeError:
                super().delete_model(request, obj)

                delete_entry(obj.name, Entity.TOPICS, optional=True)

    delete_model.short_description = "Ausgewählte Themen löschen"

# Register your model here
admin.site.register(Topic, TopicAdmin)
