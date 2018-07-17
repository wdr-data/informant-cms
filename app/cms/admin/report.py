import os
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.utils import timezone
from django import forms
from emoji_picker.widgets import EmojiPickerTextInput
from tags_input import admin as tags_input_admin
import requests
from django.db import transaction

from ..models.report import Report, ReportFragment
from .attachment import AttachmentAdmin
from .fragment import FragmentModelForm, FragmentAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm

AMP_TRIGGER_URL = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateReport')

class ReportFragmentModelForm(FragmentModelForm):

    class Meta:
        model = ReportFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_note', 'link_wiki']


class ReportFragmentAdminInline(FragmentAdminInline):
    model = ReportFragment
    form = ReportFragmentModelForm

    extra = 1


class ReportModelForm(NewsBaseModelForm):

    headline = forms.CharField(label='Überschrift', widget=EmojiPickerTextInput, max_length=200)

    delivered = forms.BooleanField(
        label='Versendet',
        help_text="Wurde diese Meldung bereits in einem Highlights-Push vom Bot versendet?",
        disabled=True,
        required=False)

    class Meta:
        model = Report
        fields = ['headline', 'short_headline', 'genres', 'tags', 'text', 'media',
                  'media_original', 'media_note', 'created', 'published', 'delivered']


class ReportAdmin(NewsBaseAdmin):
    form = ReportModelForm
    date_hierarchy = 'created'
    list_filter = ['published']
    search_fields = ['headline', 'short_headline']
    list_display = ('published', 'headline', 'short_headline', 'created')
    list_display_links = ('headline', )
    inlines = (ReportFragmentAdminInline, )

    def save_model(self, request, obj, form, change):
        obj.modified = timezone.now()
        if obj.published and obj.published_date is None:
            obj.published_date = timezone.now()

        super().save_model(request, obj, form, change)

        if obj.published and os.environ.get('AMP_SERVICE_ENDPOINT'):

            def commit_hook():
                sleep(1)  # Wait for DB
                r = requests.post(
                    url=AMP_TRIGGER_URL,
                    json={'id': obj.id},
                )

                if not r.ok:
                    raise Exception('AMP trigger failed: ' + r.reason)

            transaction.on_commit(commit_hook)


# Register your models here.
admin.site.register(Report, ReportAdmin)

