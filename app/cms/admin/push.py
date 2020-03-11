import os
import logging
from posixpath import join as urljoin
from time import sleep
from datetime import date, time, datetime
import re

from django.contrib import admin, messages
from django.db import transaction
from django import forms
from django.utils.http import urlencode
from emoji_picker.widgets import EmojiPickerTextareaAdmin
import requests
from django.core.exceptions import ValidationError
from admin_object_actions.admin import ModelAdminObjectActionsMixin
from admin_object_actions.forms import AdminObjectActionForm
from crum import get_current_request
import pytz

from ..models.push import Push
from ..models.report import Report
from .attachment import HasAttachmentAdmin, HasAttachmentModelForm

PUSH_TRIGGER_URLS = {
    service: urljoin(os.environ[var_name], 'push')
    for service, var_name in (('fb', 'BOT_SERVICE_ENDPOINT_FB'), ('tg', 'BOT_SERVICE_ENDPOINT_TG'))
    if var_name in os.environ
}
AMP_UPDATE_INDEX = urljoin(os.environ.get('AMP_SERVICE_ENDPOINT', ''), 'updateIndex')
MANUAL_PUSH_GROUP = os.environ.get('MANUAL_PUSH_GROUP')


class AutocompleteSelectCustom(admin.widgets.AutocompleteSelect):
    """
    Improved version of django's autocomplete select that sends an extra query parameter with the model and field name
    it is editing, allowing the search function to apply the appropriate filter.
    
    This is a modified version from the solution at https://stackoverflow.com/a/55476825 to work specifically 
    to filter by report type. Requires an overridden get_search_results on the target ModelAdmin (Report).
    """

    def __init__(self, *args, **kwargs):
        self.report_type = kwargs.pop('report_type')
        super().__init__(*args, **kwargs)

    def get_url(self):
        url = super().get_url()
        url += '?' + urlencode({
            'report_type': self.report_type.value,
        })
        return url


class PushModelForm(HasAttachmentModelForm):
    timing = forms.ChoiceField(
        required=True,
        label="Zeitpunkt",
        choices=[(Push.Timing.MORNING.value, '☕ Morgen'),
                 (Push.Timing.EVENING.value, '🌙 Abend')],
        help_text='Um Breaking News zu senden, bitte direkt in der Meldung auswählen.')
    intro = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextareaAdmin, max_length=950)
    outro = forms.CharField(
        required=True, label="Outro-Text", widget=EmojiPickerTextareaAdmin, max_length=950)

    report_0 = forms.ModelChoiceField(
        Report.objects.filter(type='regular'),
        label='Meldung 1',
        required=True, 
        help_text='Hier die erste Meldung auswählen.',
        widget=AutocompleteSelectCustom(
            Push.reports.field.remote_field, 
            admin.site,
            report_type=Report.Type.REGULAR,
        ))

    report_1 = forms.ModelChoiceField(
        Report.objects.filter(type='regular'),
        label='Meldung 2',
        required=True,
        help_text='Hier die zweite Meldung auswählen.',
        widget=AutocompleteSelectCustom(
            Push.reports.field.remote_field, 
            admin.site,
            report_type=Report.Type.REGULAR,
        ))

    report_2 = forms.ModelChoiceField(
        Report.objects.filter(type='regular'),
        label='Meldung 3',
        required=True,
        help_text='Hier die dritte Meldung auswählen.',
        widget=AutocompleteSelectCustom(
            Push.reports.field.remote_field, 
            admin.site,
            report_type=Report.Type.REGULAR,
        ))

    last_report = forms.ModelChoiceField(
        Report.objects.filter(type='last'),
        label='Zum Schluss',
        required=False,
        help_text='Optional: Hier für den Abend-Push die bunte Meldung auswählen.',
        widget=AutocompleteSelectCustom(
            Push.reports.field.remote_field, 
            admin.site,
            report_type=Report.Type.LAST,
        ))

    class Meta:
        model = Push
        exclude = ()

    def get_initial_for_field(self, field, field_name):
        # Fill report_n fields from m2m
        pattern = r'report_(\d)'
        match = re.match(pattern, field_name)

        if match:
            try:
                return self.instance.reports.all()[int(match.group(1))]
            except (ValueError, IndexError):
                return None

        return super().get_initial_for_field(field, field_name)

    def clean(self):
        # Merge reports from separate fields into list
        reports = []

        for i in range(3):
            report = self.cleaned_data.get(f'report_{i}')

            if not report:
                continue

            if report in reports:
                raise ValidationError({f'report_{i}': 'Meldungen dürfen nicht doppelt vorkommen!'})

            reports.append(report)

        self.cleaned_data['reports'] = reports
        return self.cleaned_data

    def _save_m2m(self, *args, **kwargs):
        # Add 'fake' reports field to meta so it will be saved
        self._meta.fields.append('reports')
        super()._save_m2m(*args, **kwargs)


class SendManualForm(AdminObjectActionForm):

    confirm = forms.BooleanField(
        required=True,
        help_text='''Nur manuell senden, falls ein Push nicht automatisch versendet wurde, weil er z. B. nicht rechtzeitig freigegeben wurde.
        Falls in einem Kanal bereits gesendet wurde, wird in diesem Kanal nicht noch einmal versendet.''',
        label='Ja, ich möchte wirklich den Push manuell versenden',
    )

    class Meta:
        model = Push
        fields = ()

    def do_object_action(self):
        failed = []
        for service, push_trigger_url in PUSH_TRIGGER_URLS.items():
            if Push.DeliveryStatus(getattr(self.instance, f'delivered_{service}')) is not Push.DeliveryStatus.NOT_SENT:
                continue

            r = requests.post(
                url=push_trigger_url,
                json={
                    'push': self.instance.id,
                    'manual': True,
                }
            )

            if not r.ok:
                failed.append(service.upper())

        if failed:
            raise Exception(f'Manuelles Senden für mindestens einen Bot ist fehlgeschlagen ({", ".join(failed)})')


class PushAdmin(ModelAdminObjectActionsMixin, HasAttachmentAdmin):
    form = PushModelForm
    change_form_template = "admin/cms/change_form_publish_direct.html"
    fields = (
        'display_object_actions_detail', 'published', 'timing', 'pub_date', 'headline',
        'intro', 'report_0', 'report_1', 'report_2', 'last_report', 'outro', 
        'attachment', 'attachment_preview',
    )
    date_hierarchy = 'pub_date'
    list_filter = ['published', 'timing']
    search_fields = ['headline']
    list_display = (
        'published', 'pub_date', 'timing', 'headline', 'send_status', 'display_object_actions_list',
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
            'verbose_name_past': 'tested',
            'form_method': 'GET',
            'function': 'preview',
        },
        {
            'slug': 'manual-push',
            'verbose_name': 'Manuell senden',
            'verbose_name_past': 'sent',
            'form_class': SendManualForm,
            'permission': 'send_manual',
        },
    ]

    def send_status(self, obj):

        if Push.DeliveryStatus(obj.delivered_fb) == Push.DeliveryStatus.NOT_SENT:
            display = 'FB: ❌'
        elif Push.DeliveryStatus(obj.delivered_fb) == Push.DeliveryStatus.SENDING:
            display = 'FB: 💬'
        else:
            display = 'FB: ✅'

        if Push.DeliveryStatus(obj.delivered_tg) == Push.DeliveryStatus.NOT_SENT:
            display += '  TG: ❌️'
        elif Push.DeliveryStatus(obj.delivered_tg) == Push.DeliveryStatus.SENDING:
            display += '  TG: 💬'
        else:
            display += '  TG: ✅'

        return display

    send_status.short_description = 'Sende-Status'

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
            obj.published
            and (
                Push.DeliveryStatus(obj.delivered_fb) is Push.DeliveryStatus.NOT_SENT
                or Push.DeliveryStatus(obj.delivered_tg) is Push.DeliveryStatus.NOT_SENT
            )
            and obj.pub_date == date.today()
            and (
                request.user.is_superuser
                or any(group.name == MANUAL_PUSH_GROUP for group in request.user.groups.all())
            )
        )

    def save_model(self, request, obj, form, change):
        local_time = datetime.now(tz=pytz.timezone('Europe/Berlin'))
        if obj.pub_date < local_time.date():
            messages.warning(
                request,
                'Das Push-Datum für diesen Push liegt in der Vergangenheit. '
                'Dieser Push wird daher nicht gesendet. Bitte Datum prüfen!'
            )
        elif (obj.pub_date == local_time.date()
                and local_time.time() > time(10, 00)
                and Push.Timing(obj.timing) is Push.Timing.MORNING):
            messages.warning(
                request,
                'Der Push hat das Datum von heute, ist aber ein Morgen-Push. '
                'Dieser Push wird daher nicht gesendet. Bitte Datum prüfen!'
            )

        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_publish-save" in request.POST:
            obj.published = True
            obj.save()
            self.message_user(
                request,
                f'Der {"Morgen-" if obj.timing == Push.Timing.MORNING.value else "Abend-"}Push ist freigegeben.'
            )
        return super().response_change(request, obj)


# Register your models here.
admin.site.register(Push, PushAdmin)
