from django.contrib import admin

from ..models.subtype import Subtype

class SubtypeAdmin(admin.ModelAdmin):
    class Meta:
        model = Subtype
        fields = "__all__"

# Register your model here
admin.site.register(Subtype, SubtypeAdmin)
