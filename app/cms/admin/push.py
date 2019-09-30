import os
import logging
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.db import transaction
from django import forms
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
from emoji_picker.widgets import EmojiPickerTextareaAdmin
import requests
from django.core.exceptions import ValidationError
from crum import get_current_request

from ..models.push import Push
from .attachment import AttachmentAdmin

PUSH_TRIGGER_URL = urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'push')
AMP_UPDATE_INDEX = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateIndex')


class PushModelForm(forms.ModelForm):
    timing = forms.ChoiceField(
        required=True,
        label="Zeitpunkt",
        choices=[(Push.Timing.MORNING.value, '🌇 Morgen'),
                 (Push.Timing.EVENING.value, '🌆 Abend')],
        help_text='Um Breaking News zu senden, bitte direkt in der Meldung auswählen.')
    intro = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextareaAdmin, max_length=1000)
    outro = forms.CharField(
        required=True, label="Outro-Text", widget=EmojiPickerTextareaAdmin, max_length=2000)

    delivered = forms.BooleanField(
        label='Versendet', help_text="Wurde dieser Push bereits versendet?", disabled=True,
        required=False)

    class Meta:
        model = Push
        exclude = ()

    def clean(self):
        """Validate number of reports"""
        reports = list(self.cleaned_data.get('reports', []))
        if len(reports) > 4:
            raise ValidationError("Ein Push darf nicht mehr als 4 Meldungen enthalten!")
        return self.cleaned_data


class PushAdmin(AttachmentAdmin):
    form = PushModelForm
    fields = (
        'display_object_actions_detail', 'pub_date', 'timing', 'headline', 'intro', 'reports',
        'outro', 'media', 'media_original', 'media_alt', 'media_note', 'published', 'delivered',
    )
    date_hierarchy = 'pub_date'
    list_filter = ['published', 'timing']
    search_fields = ['headline']
    list_display = (
        'published', 'pub_date', 'timing', 'headline', 'delivered', 'display_object_actions_list',
    )
    readonly_fields = (
        'display_object_actions_detail',
    )
    list_display_links = ('pub_date', )
    ordering = ('-pub_date', )

    def display_object_actions_list(self, obj=None):
        return self.display_object_actions(obj, list_only=True)
    display_object_actions_list.short_description = 'Aktionen'

    def display_object_actions_detail(self, obj=None):
        return self.display_object_actions(obj, detail_only=True)
    display_object_actions_detail.short_description = 'Aktionen'

    object_actions = [
        {
            'slug': 'preview-push',
            'verbose_name': 'Testen',
            'verbose_name_past': 'getestet',
            'form_method': 'GET',
            'function': 'preview',
        },
    ]

    def preview(self, obj, form):
        request = get_current_request()

        error_message = 'Bitte trage deine PSID in deinem Profil ein'
        try:
            if not request.user.profile.psid:
                raise Exception(error_message)
        except:
            raise Exception(error_message)

        r = requests.post(
            url=PUSH_TRIGGER_URL,
            json={
                'push': obj.id,
                'preview': request.user.profile.psid,
            }
        )

        if not r.ok:
            raise Exception('Nicht erfolgreich')

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ('reports', ):
            kwargs['widget'] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        try:
            last_push = obj.__class__.last(delivered=True, breaking=False)[0]
        except:
            last_push = None

        was_last_push = last_push and last_push.id == obj.id

        super().save_model(request, obj, form, change)

        try:
            last_push = obj.__class__.last(delivered=True, breaking=False)[0]
        except:
            last_push = None

        is_last_push = last_push and last_push.id == obj.id

        def update_index():
            if not last_push:
                return

            sleep(1)  # Wait for DB
            r = requests.post(
                url=AMP_UPDATE_INDEX,
                json={'id': last_push.id})

            if not r.ok:
                logging.error('Index-Site update trigger failed: ' + r.reason)

        if is_last_push and os.environ.get('AMP_SERVICE_ENDPOINT'):
            transaction.on_commit(update_index)

        elif was_last_push and not is_last_push and os.environ.get('AMP_SERVICE_ENDPOINT'):
            transaction.on_commit(update_index)


    def delete_model(self, request, obj):
        try:
            last_push = obj.__class__.last(delivered=True, breaking=False)[0]
        except:
            last_push = None

        was_last_push = last_push and last_push.id == obj.id

        super().delete_model(request, obj)

        try:
            last_push = obj.__class__.last(delivered=True, breaking=False)[0]
        except:
            last_push = None

        is_last_push = last_push and last_push.id == obj.id

        if was_last_push and not is_last_push and os.environ.get('AMP_SERVICE_ENDPOINT'):
            def update_index():
                if not last_push:
                    return

                sleep(1)  # Wait for DB
                r = requests.post(
                    url=AMP_UPDATE_INDEX,
                    json={'id': last_push.id})

                if not r.ok:
                    logging.error('Index-Site update trigger failed: ' + r.reason)

            transaction.on_commit(update_index)


# Register your models here.
admin.site.register(Push, PushAdmin)
