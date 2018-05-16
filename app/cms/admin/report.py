from django.contrib import admin
from django import forms
from tags_input import admin as tags_input_admin

from ..models.report import Report, ReportFragment
from .attachment import AttachmentAdmin
from .fragment import FragmentModelForm, FragmentAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm


class ReportFragmentModelForm(FragmentModelForm):

    class Meta:
        model = ReportFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_note', 'link_wiki']


class ReportFragmentAdminInline(FragmentAdminInline):
    model = ReportFragment
    form = ReportFragmentModelForm

    extra = 1


class ReportModelForm(NewsBaseModelForm):

    delivered = forms.BooleanField(
        label='Versendet',
        help_text="Wurde diese Meldung bereits in einem Highlights-Push vom Bot versendet?",
        disabled=True,
        required=False)

    class Meta:
        model = Report
        fields = ['headline', "genres", 'topic', 'tags', 'text', 'media', 'media_original',
                  'media_note', 'created', 'published', 'delivered']


class ReportAdmin(NewsBaseAdmin):
    form = ReportModelForm
    date_hierarchy = 'created'
    list_filter = ['published']
    search_fields = ['headline']
    list_display = ('headline', 'created', 'published')
    inlines = (ReportFragmentAdminInline, )


# Register your models here.
admin.site.register(Report, ReportAdmin)

