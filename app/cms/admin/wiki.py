from django.contrib import admin

from ..models.wiki import Wiki, WikiFragment
from .fragment import FragmentModelForm, FragmentAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm


class WikiFragmentModelForm(FragmentModelForm):

    class Meta:
        model = WikiFragment
        fields = ['question', 'text', 'attachment', 'attachment_preview', 'link_wiki']


class WikiFragmentAdminInline(FragmentAdminInline):
    model = WikiFragment
    form = WikiFragmentModelForm

    fk_name = 'wiki'


class WikiModelForm(NewsBaseModelForm):
    class Meta:
        model = Wiki
        fields = ['name', 'follow_up_at', 'genres',
                  'tags', 'text', 'attachment', 'attachment_preview']


class WikiAdmin(NewsBaseAdmin):
    form = WikiModelForm
    search_fields = ['name']
    list_display = ('name', 'get_genres', 'follow_up_at')
    inlines = (WikiFragmentAdminInline, )
    ordering = ('follow_up_at',)

    def get_genres(self, obj):
        return ', '.join(str(genre) for genre in obj.genres.all())
    get_genres.short_description = 'Genres'


# Register your models here.
admin.site.register(Wiki, WikiAdmin)
