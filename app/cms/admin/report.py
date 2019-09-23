import os
import logging
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from emoji_picker.widgets import EmojiPickerTextInput
from tags_input import admin as tags_input_admin
import requests
from django.db import transaction

from ..models.report import Report, ReportFragment, ReportQuiz
from .attachment import AttachmentAdmin
from .fragment import FragmentModelForm, FragmentAdminInline
from .quiz import QuizModelForm, QuizAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm

AMP_UPDATE_REPORT = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateReport')
AMP_DELETE_REPORT = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'deleteReport')


class ReportFragmentModelForm(FragmentModelForm):

    class Meta:
        model = ReportFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_alt', 'media_note',
                  'link_wiki']


class ReportFragmentAdminInline(FragmentAdminInline):
    model = ReportFragment
    form = ReportFragmentModelForm

    extra = 1


class ReportQuizModelForm(QuizModelForm):

    class Meta:
        model = ReportQuiz
        fields = ['correct_option', 'quiz_option', 'quiz_text', 'media', 'media_original',
                  'media_alt', 'media_note']


class ReportQuizInlineFormset(forms.models.BaseInlineFormSet):
    def is_valid(self):
        return super().is_valid() and not any([bool(e) for e in self.errors])

    def clean(self):

        super().clean()

        # get forms that actually have valid data
        option_count = 0
        correct_option_count = 0

        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    option_count += 1
                    if form.cleaned_data['correct_option']:
                        correct_option_count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if option_count == 1:
            raise forms.ValidationError(
                'Es müssen mindestens 2 Antworten für ein Quiz existieren!')
        elif option_count > 1 and correct_option_count == 0:
            raise forms.ValidationError(
                'Es gibt keine richtige Antwort!')
        elif option_count > 1 and correct_option_count != 1:
            raise forms.ValidationError(
                'Es gibt mehr als eine richtige Antwort!')


class ReportQuizAdminInline(QuizAdminInline):
    model = ReportQuiz
    form = ReportQuizModelForm
    formset = ReportQuizInlineFormset

    extra = 0
    max_num = 3


class ReportModelForm(NewsBaseModelForm):

    headline = forms.CharField(label='Überschrift', widget=EmojiPickerTextInput, max_length=200)

    delivered = forms.BooleanField(
        label='Versendet',
        help_text="Wurde diese Meldung bereits in einem Highlights-Push vom Bot versendet?",
        disabled=True,
        required=False)

    media_alt = forms.CharField(
        label='Alternativ-Text',
        help_text='Beschreibung des Bildes/Gifs für Blinde.',
        max_length=125,
        required=False
    )

    class Meta:
        model = Report
        fields = ['headline', 'short_headline', 'genres', 'tags', 'media',
                  'media_original', 'media_alt', 'media_note', 'text', 'link', 'created', 'published', 'delivered']


class ReportAdmin(NewsBaseAdmin):
    form = ReportModelForm
    date_hierarchy = 'created'
    list_filter = ['published']
    search_fields = ['headline', 'short_headline']
    list_display = ('published', 'headline', 'short_headline', 'created')
    list_display_links = ('headline', )
    inlines = (ReportFragmentAdminInline, ReportQuizAdminInline, )

    def save_model(self, request, obj, form, change):
        obj.modified = timezone.now()
        if obj.published and obj.published_date is None:
            obj.published_date = timezone.now()

        original = None
        if obj.pk:
            original = obj.__class__.objects.get(pk=obj.pk)

        if not obj.author:
            obj.author = request.user.get_full_name()

        super().save_model(request, obj, form, change)

        if obj.published and os.environ.get('AMP_SERVICE_ENDPOINT'):

            def commit_hook():
                sleep(1)  # Wait for DB
                r = requests.post(
                    url=AMP_UPDATE_REPORT,
                    json={'id': obj.id},
                )

                if not r.ok:
                    logging.error('AMP update trigger failed: ' + r.reason)

            transaction.on_commit(commit_hook)
        elif original and not obj.published and original.published and os.environ.get('AMP_SERVICE_ENDPOINT'):
            def commit_hook():
                sleep(1)  # Wait for DB
                r = requests.post(
                    url=AMP_DELETE_REPORT,
                    json={
                        'id': obj.id,
                        'created': obj.created.isoformat(),
                    },
                )

                if not r.ok:
                    logging.error('AMP delete trigger failed: ' + r.reason)

            transaction.on_commit(commit_hook)

    def delete_model(self, request, obj):
        id = obj.id
        super().delete_model(request, obj)

        if obj.published and os.environ.get('AMP_SERVICE_ENDPOINT'):

            def commit_hook():
                sleep(1)  # Wait for DB
                r = requests.post(
                    url=AMP_DELETE_REPORT,
                    json={
                        'id': id,
                        'created': obj.created.isoformat(),
                    },
                )

                if not r.ok:
                    logging.error('AMP delete trigger failed: ' + r.reason)

            transaction.on_commit(commit_hook)


# Register your models here.
admin.site.register(Report, ReportAdmin)

