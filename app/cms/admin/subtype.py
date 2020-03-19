from django.contrib import admin

from ..models.subtype import Subtype

class SubtypeAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'emoji', 'type']

    class Meta:
        model = Subtype
        fields = "__all__"

    def get_search_results(self, request, queryset, search_term):
        '''
        Custom search results function that allows the autocomplete field in the ReportModelForm
        to filter for specific reports (facilitated by the toggle_subtype.js script).
        '''
        if 'report_type' in request.GET:
            queryset = queryset.filter(type=request.GET['report_type'])
        return super().get_search_results(request, queryset, search_term)


# Register your model here
admin.site.register(Subtype, SubtypeAdmin)
