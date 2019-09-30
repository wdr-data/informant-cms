import os
import logging
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from emoji_picker.widgets import EmojiPickerTextInputAdmin
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
ATTACHMENT_TRIGGER_URL = urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'attachment')
BREAKING_TRIGGER_URL = urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'breaking')


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

    headline = forms.CharField(label='Überschrift', widget=EmojiPickerTextInputAdmin, max_length=200)

    delivered = forms.BooleanField(
        label='Breaking erfolgreich versendet',
        help_text='Dieses Feld wird nur markiert, '
                  'wenn eine Meldung vom Meldungstyp "Breaking" erfolgreich versendet wurde.',
        required=False)

    media_alt = forms.CharField(
        label='Alternativ-Text',
        help_text='Beschreibung des Bildes/Gifs für Blinde.',
        max_length=125,
        required=False
    )

    class Meta:
        model = Report
        fields = ['type', 'published', 'headline', 'short_headline', 'genres', 'tags', 'media',
                  'media_original', 'media_alt', 'media_note', 'text', 'audio',
                  'link']


class ReportAdmin(NewsBaseAdmin):
    form = ReportModelForm
    date_hierarchy = 'created'
    list_filter = ['published', 'type']
    search_fields = ['headline']
    list_display = ('typ_status' , 'headline', 'short_headline', 'created',)
    list_display_links = ('headline', )
    inlines = (ReportFragmentAdminInline, ReportQuizAdminInline, )

    def typ_status(self, obj):
        if Report.Type(obj.type) == Report.Type.BREAKING:
            display = '🚨'
        else:
            display = '📰'
        if not obj.published:
            display += ' -  ✏️'
        elif not obj.delivered:
            display += ' -  ✅'
        elif obj.delivered:
            display += ' -  📤'

        return display

    def save_model(self, request, obj, form, change):
        obj.modified = timezone.now()
        if obj.published and obj.published_date is None:
            obj.published_date = timezone.now()

        original = None
        if obj.pk:
            original = obj.__class__.objects.get(pk=obj.pk)

        if not obj.author:
            obj.author = request.user.get_full_name()

        if 'audio' in form.changed_data and obj.audio:
            audio_url = str(obj.audio)

            filename = audio_url.split('/')[-1]
            if not (filename.lower().endswith('.mp3')):
                messages.error(
                    request,
                    f'Das Audio hat das Falsche Format. Aktzeptierte Formate: *.mp3'
                )
                obj.audio = None

            else:
                r = requests.post(
                    ATTACHMENT_TRIGGER_URL,
                    json={'url': audio_url}
                )

                if r.status_code == 200:
                    messages.success(
                        request, f'Anhang {obj.audio} wurde zu Facebook hochgeladen 👌')

                else:
                    messages.error(
                        request,
                        f'Anhang {obj.audio} konnte nicht zu Facebook hochgeladen werden')

                    obj.audio = None

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

        try:
            if Report.Type(obj.type) is Report.Type.BREAKING and obj.published and not obj.delivered:

                def commit_hook():
                    sleep(1)  # Wait for DB
                    r = requests.post(
                        url=BREAKING_TRIGGER_URL,
                        json={
                            'report': obj.id,
                        }
                    )

                    if r.status_code == 200:
                        messages.success(request, '🚨 Breaking wird jetzt gesendet...')

                    else:
                        messages.error(request, '🚨 Breaking konnte nicht gesendet werden!')

                transaction.on_commit(commit_hook)

        except Exception as e:
            messages.error(request, str(e))

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

