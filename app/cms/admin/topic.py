from django.contrib import admin

from ..models.topic import Topic


class TopicAdmin(admin.ModelAdmin):

    class Meta:
        model = Topic
        fields = "__all__"


# Register your model here
admin.site.register(Topic, TopicAdmin)
