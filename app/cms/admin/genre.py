from django.contrib import admin

from ..models.genre import Genre


class GenreAdmin(admin.ModelAdmin):

    class Meta:
        model = Genre
        fields = "__all__"


# Register your model here
admin.site.register(Genre, GenreAdmin)
