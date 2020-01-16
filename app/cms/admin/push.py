import os
import logging
from posixpath import join as urljoin
from time import sleep
from datetime import date

from django.contrib import admin, messages
from django.db import transaction
from django import forms
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
from emoji_picker.widgets import EmojiPickerTextareaAdmin
import requests
from django.core.exceptions import ValidationError
from admin_object_actions.admin import ModelAdminObjectActionsMixin
from admin_object_actions.forms import AdminObjectActionForm
from crum import get_current_request

from ..models.push import Push
from .attachment import AttachmentAdmin

PUSH_TRIGGER_URLS = [
    urljoin(os.environ[var_name], 'push')
    for var_name in ('BOT_SERVICE_ENDPOINT_FB', 'BOT_SERVICE_ENDPOINT_TG')
    if var_name in os.environ
]
AMP_UPDATE_INDEX = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateIndex')
MANUAL_PUSH_GROUP = os.environ.get('MANUAL_PUSH_GROUP')


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


class SendManualForm(AdminObjectActionForm):

    confirm = forms.BooleanField(
        required=True,
        help_text='Nur manuell senden, falls ein Push nicht automatisch versendet wurde, weil er z. B. nicht rechtzeitig freigegeben wurde.',
        label='Ja, ich möchte wirklich den Push manuell versenden',
    )

    class Meta:
        model = Push
        fields = ()

    def do_object_action(self):
        failed = []
        for push_trigger_url in PUSH_TRIGGER_URLS:
            r = requests.post(
                url=push_trigger_url,
                json={
                    'push': self.instance.id,
                    'manual': True,
                }
            )

            if not r.ok:
                failed.append(push_trigger_url)

        if failed:
            raise Exception(f'Manuelles Senden für mindestens einen Bot ist fehlgeschlagen ({", ".join(failed)})')


class PushAdmin(ModelAdminObjectActionsMixin, AttachmentAdmin):
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
        {
            'slug': 'manual-push',
            'verbose_name': 'Manuell senden',
            'verbose_name_past': 'gesendet',
            'form_class': SendManualForm,
            'permission': 'send_manual',
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
            url=urljoin(os.environ['BOT_SERVICE_ENDPOINT_FB'], 'push'),
            json={
                'push': obj.id,
                'preview': request.user.profile.psid,
            }
        )

        if not r.ok:
            raise Exception('Nicht erfolgreich')

    def has_send_manual_permission(self, request, obj=None):
        return (
            obj.published and
            not obj.delivered and
            obj.pub_date == date.today() and
            (
                request.user.is_superuser or
                any(group.name == MANUAL_PUSH_GROUP for group in request.user.groups.all())
            )
        )

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
