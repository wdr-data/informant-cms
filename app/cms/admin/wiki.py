from django.contrib import admin

from ..models.wiki import Wiki, WikiFragment
from .fragment import FragmentModelForm, FragmentAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm


class WikiFragmentModelForm(FragmentModelForm):

    class Meta:
        model = WikiFragment
        fields = ['question', 'text', 'media', 'media_original',
                  'media_note', 'link_wiki']


class WikiFragmentAdminInline(FragmentAdminInline):
    model = WikiFragment
    form = WikiFragmentModelForm

    fk_name = 'wiki'


class WikiModelForm(NewsBaseModelForm):
    class Meta:
        model = Wiki
        fields = ['name', 'follow_up_at', 'genres',
                  'topic', 'tags', 'text', 'media', 'media_original',
                  'media_note']


class WikiAdmin(NewsBaseAdmin):
    form = WikiModelForm
    search_fields = ['name']
    list_display = ('name', 'get_genres', 'topic', 'follow_up_at')
    inlines = (WikiFragmentAdminInline, )
    ordering = ('follow_up_at',)

    def get_genres(self, obj):
        return ', '.join(str(genre) for genre in obj.genres.all())
    get_genres.short_description = 'Genres'


# Register your models here.
admin.site.register(Wiki, WikiAdmin)
