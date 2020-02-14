import asyncio
import os
import logging
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.utils import timezone
from django import forms
from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin
import requests
from django.db import transaction
from admin_object_actions.admin import ModelAdminObjectActionsMixin
from crum import get_current_request

from ..models.report import Report, ReportFragment, ReportQuiz
from .attachment import trigger_attachments
from .fragment import FragmentModelForm, FragmentAdminInline
from .quiz import QuizModelForm, QuizAdminInline
from .news_base import NewsBaseAdmin, NewsBaseModelForm

AMP_UPDATE_REPORT = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateReport')
AMP_DELETE_REPORT = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'deleteReport')
BREAKING_TRIGGER_URLS = [
    urljoin(os.environ[var_name], 'breaking')
    for var_name in ('BOT_SERVICE_ENDPOINT_FB', 'BOT_SERVICE_ENDPOINT_TG')
    if var_name in os.environ
]


class ReportFragmentModelForm(FragmentModelForm):

    class Meta:
        model = ReportFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_alt', 'media_note',
                  'link_wiki']


class ReportFragmentAdminInline(FragmentAdminInline):
    model = ReportFragment
    form = ReportFragmentModelForm
    fields = ['question', 'media', 'media_original', 'media_alt', 'media_note', 'text']
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

    summary = forms.CharField(label='Telegram-Text', widget=EmojiPickerTextareaAdmin, max_length=900)

    media_alt = forms.CharField(
        label='Alternativ-Text',
        help_text='Beschreibung des Bildes/Gifs für Blinde.',
        max_length=125,
        required=False
    )

    class Meta:
        model = Report
        exclude = ()


class ReportAdmin(ModelAdminObjectActionsMixin, NewsBaseAdmin):
    form = ReportModelForm
    change_form_template = "admin/cms/change_form_publish_direct.html"
    date_hierarchy = 'created'
    list_filter = ['published', 'type']
    search_fields = ['headline']
    list_display = (
        'report_type',
        'status',
        'headline',
        'created',
        'assets',
        'send_status',
        'display_object_actions_list',
    )
    fields = (
        'display_object_actions_detail', 'type', 'published', 'headline', 'summary', 'short_headline',
        'genres', 'tags', 'media', 'media_original', 'media_alt', 'media_note', 'text',
        'link',
    )
    # value 'audio' is supposed to be added to fields again, once the feature is communicated
    readonly_fields = (
        'display_object_actions_detail',
    )
    list_display_links = ('headline', )
    inlines = (ReportFragmentAdminInline, ReportQuizAdminInline, )

    def display_object_actions_list(self, obj=None):
        return self.display_object_actions(obj, list_only=True)
    display_object_actions_list.short_description = 'Aktionen'

    def display_object_actions_detail(self, obj=None):
        return self.display_object_actions(obj, detail_only=True)
    display_object_actions_detail.short_description = 'Aktionen'

    object_actions = [
        {
            'slug': 'preview-report',
            'verbose_name': 'Testen',
            'verbose_name_past': 'getestet',
            'form_method': 'GET',
            'function': 'preview',
        },
        {
            'slug': 'breaking-report',
            'verbose_name': '🚨 Jetzt als Breaking senden',
            'verbose_name_past': 'als Breaking gesendet',
            'form_method': 'GET',
            'function': 'send_breaking',
            'permission': 'send_breaking',
        },
    ]

    def preview(self, obj, form):
        request = get_current_request()

        error_message = 'Bitte trage deine Facebook-PSID in deinem Profil ein'
        try:
            if not request.user.profile.psid:
                raise Exception(error_message)
        except:
            raise Exception(error_message)

        r = requests.post(
            url=urljoin(os.environ['BOT_SERVICE_ENDPOINT_FB'], 'breaking'),
            json={
                'report': obj.id,
                'preview': request.user.profile.psid,
            }
        )

        if not r.ok:
            raise Exception('Nicht erfolgreich')

    def has_send_breaking_permission(self, request, obj=None):
        return (
            Report.Type(obj.type) is Report.Type.BREAKING
            and obj.published
            and Report.DeliveryStatus(obj.delivered_fb) is Report.DeliveryStatus.NOT_SENT
            and Report.DeliveryStatus(obj.delivered_tg) is Report.DeliveryStatus.NOT_SENT
        )

    def send_breaking(self, obj, form):
        if self.has_send_breaking_permission(None, obj=obj):
            failed = []
            for breaking_trigger_url in BREAKING_TRIGGER_URLS:
                r = requests.post(
                    url=breaking_trigger_url,
                    json={
                        'report': obj.id,
                    }
                )

                if not r.ok:
                    failed.append(breaking_trigger_url)

            if failed:
                raise Exception(f'Breaking für mindestens einen Bot ist fehlgeschlagen ({", ".join(failed)})')
        else:
            raise Exception('Nicht erlaubt')

    def report_type(self, obj):
        if Report.Type(obj.type) == Report.Type.BREAKING:
            display = '🚨'
        elif Report.Type(obj.type) == Report.Type.REGULAR:
            display = '📰'
        elif Report.Type(obj.type) == Report.Type.LAST:
            display = '🙈'

        return display

    def status(self, obj):
        if not obj.published:
            display = '✏️'
        else:
            display = '✅'

        return display

    def send_status(self, obj):
        if not Report.Type(obj.type) == Report.Type.BREAKING:
            return ''

        if Report.DeliveryStatus(obj.delivered_fb) == Report.DeliveryStatus.NOT_SENT:
            display = 'FB: ❌️'
        elif Report.DeliveryStatus(obj.delivered_fb) == Report.DeliveryStatus.SENDING:
            display = 'FB: 💬'
        else:
            display = 'FB: ✅'

        if Report.DeliveryStatus(obj.delivered_tg) == Report.DeliveryStatus.NOT_SENT:
            display += '  TG: ❌'
        elif Report.DeliveryStatus(obj.delivered_tg) == Report.DeliveryStatus.SENDING:
            display += '  TG: 💬'
        else:
            display += '  TG: ✅'

        return display

    send_status.short_description = 'Sende-Status'
    report_type.short_description = 'Typ'
    status.short_description = 'Status'

    def assets(self, obj):
        assets = ''
        if obj.media and str(obj.media) != '':
            assets = '🖼️'

        if obj.link and str(obj.link) != '':
            assets += '🔗️'

        if obj.audio and str(obj.audio) != '':
            assets += '🔊'

        return assets

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
                success = trigger_attachments(audio_url)

                if success:
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

    def response_change(self, request, obj):
        if "_publish-save" in request.POST:
            obj.published = True
            obj.save()
            self.message_user(request, "Die Meldung ist freigegeben.")
        return super().response_change(request, obj)


# Register your models here.
admin.site.register(Report, ReportAdmin)
