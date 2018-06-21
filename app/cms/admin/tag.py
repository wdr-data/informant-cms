from django.contrib import admin

from ..models.tag import ReportTag


class ReportTagAdmin(admin.ModelAdmin):

    search_fields = ['name']

    class Meta:
        model = ReportTag
        fields = "__all__"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# Register your model here
admin.site.register(ReportTag, ReportTagAdmin)
