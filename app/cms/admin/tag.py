from django.contrib import admin

from ..models.tag import ReportTag


class ReportTagAdmin(admin.ModelAdmin):

    search_fields = ['name']

    class Meta:
        model = ReportTag
        fields = "__all__"


# Register your model here
admin.site.register(ReportTag, ReportTagAdmin)
