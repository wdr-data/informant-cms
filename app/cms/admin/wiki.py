from django.contrib import admin
from django import forms
from tags_input import admin as tags_input_admin

from ..models.wiki import Wiki, WikiFragment
from .attachment import AttachmentAdmin, DisplayImageWidgetTabularInline, DisplayImageWidgetStackedInline


class WikiFragmentModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Text", widget=forms.Textarea, max_length=640)

    class Meta:
        model = WikiFragment
        fields = ['question', 'text', 'media', 'media_original',
                  'media_note', 'link_wiki']


class WikiFragmentAdminInline(DisplayImageWidgetStackedInline):
    image_display_fields = ['media']
    model = WikiFragment
    form = WikiFragmentModelForm

    fk_name = 'wiki'
    extra = 1


class WikiModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Intro-Text", widget=forms.Textarea, max_length=640)

    class Meta:
        model = Wiki
        fields = ['name', 'follow_up_at', 'genres',
                  'topic', 'tags', 'text', 'media', 'media_original',
                  'media_note']


class WikiAdmin(tags_input_admin.TagsInputAdmin, AttachmentAdmin):
    form = WikiModelForm
    search_fields = ['name']
    list_display = ('name', 'get_genres', 'topic', 'follow_up_at')
    inlines = (WikiFragmentAdminInline, )
    tag_fields = ['tags']
    ordering = ('follow_up_at',)

    def get_genres(self, obj):
        return ', '.join(str(genre) for genre in obj.genres.all())
    get_genres.short_description = 'Genres'

# Register your models here.
admin.site.register(Wiki, WikiAdmin)
