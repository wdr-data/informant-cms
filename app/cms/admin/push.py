import os
import logging
from posixpath import join as urljoin
from time import sleep

from django.contrib import admin, messages
from django.db import transaction
from django import forms
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
from emoji_picker.widgets import EmojiPickerTextarea
import requests
from django.core.exceptions import ValidationError

from ..models.push import Push
from .attachment import AttachmentAdmin

PUSH_TRIGGER_URL = urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'push')
AMP_UPDATE_INDEX = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateIndex')


class PushModelForm(forms.ModelForm):
    intro = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextarea, max_length=1000)
    outro = forms.CharField(
        required=True, label="Outro-Text", widget=EmojiPickerTextarea, max_length=2000)

    delivered = forms.BooleanField(
        label='Versendet', help_text="Wurde dieser Push bereits versendet?", disabled=True,
        required=False)

    class Meta:
        model = Push
        fields = ('pub_date', 'timing', 'headline', 'intro', 'reports',
                  'outro', 'media', 'media_original', 'media_alt', 'media_note',
                  'published', 'delivered')

    def clean(self):
        """Validate number of reports"""
        reports = list(self.cleaned_data.get('reports', []))
        if len(reports) > 4:
            raise ValidationError("Ein Push darf nicht mehr als 4 Meldungen enthalten!")
        return self.cleaned_data


class PushAdmin(AttachmentAdmin):
    form = PushModelForm
    date_hierarchy = 'pub_date'
    list_filter = ['published', 'timing']
    search_fields = ['headline']
    list_display = ('published', 'pub_date', 'timing', 'headline', 'delivered')
    list_display_links = ('pub_date', )
    ordering = ('-pub_date',)

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

        try:
            if obj.timing == Push.Timing.BREAKING.value and obj.published and not obj.delivered:

                def commit_hook():
                    sleep(1)  # Wait for DB
                    r = requests.post(
                        url=PUSH_TRIGGER_URL,
                        json={'timing': Push.Timing.BREAKING.value}
                    )

                    if r.status_code == 200:
                        messages.success(request, '🚨 Breaking wird jetzt gesendet...')

                    else:
                        messages.error(request, '🚨 Breaking konnte nicht gesendet werden!')

                transaction.on_commit(commit_hook)

        except Exception as e:
            messages.error(request, str(e))

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
