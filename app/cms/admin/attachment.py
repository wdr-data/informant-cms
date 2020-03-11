import asyncio
import logging
import os
import requests
from posixpath import join as urljoin
from os.path import splitext

import httpx
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from raven.contrib.django.raven_compat.models import client

from ..models.attachment import Attachment

ATTACHMENT_TRIGGER_URLS = [
    urljoin(os.environ[var_name], 'attachment')
    for var_name in ('BOT_SERVICE_ENDPOINT_FB', 'BOT_SERVICE_ENDPOINT_TG')
    if var_name in os.environ
]

IMAGE_PROCESSING_FAILED = 'Automatische Bildverarbeitung fehlgeschlagen'


async def _trigger_attachments(url):
    async with httpx.AsyncClient() as client:
        coroutines = [
            client.post(trigger, json={'url': url}, timeout=26.0)
            for trigger in ATTACHMENT_TRIGGER_URLS
        ]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
    return results


def trigger_attachments(url):
    results = asyncio.run(_trigger_attachments(url))

    failed = False
    for result in results:
        if isinstance(result, Exception):
            failed = True
            try:
                raise result
            except:
                client.captureException()

    return not failed and all(result.status_code == 200 for result in results)


class AdminDisplayImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img style="max-height: 200px; max-width: 350px;" '
                f'src="{image_url}" alt="{file_name}" /></a>')

        # Don't add super() widget which would display the file upload field

        return mark_safe(''.join(output))


class DisplayImageWidgetMixin(object):
    image_display_fields = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.image_display_fields:
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminDisplayImageWidget
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


class DisplayImageWidgetAdmin(DisplayImageWidgetMixin, admin.ModelAdmin):
    pass


class DisplayImageWidgetStackedInline(DisplayImageWidgetMixin, admin.StackedInline):
    pass


class DisplayImageWidgetTabularInline(DisplayImageWidgetMixin, admin.TabularInline):
    pass

class AttachmentModelForm(forms.ModelForm):

    class Meta:
        model = Attachment
        exclude = ['upload_date']

    def clean(self):
        obj = self.instance
        if ('original' in self.changed_data
                or 'credit' in self.changed_data
                or not obj
                or obj.original and not obj.processed):
            try:
                path, url = Attachment.process_attachment(
                    self.cleaned_data.get('original'),
                    self.cleaned_data.get('credit'),
                )

            except:
                logging.exception('%s', obj.original)
                raise ValidationError({f'original': 'Bildverarbeitung fehlgeschlagen!'})

            else:

                success = trigger_attachments(url)

                if success:
                    self.cleaned_data['processed'] = path
                    self.changed_data = ['processed']

                else:
                    raise ValidationError({f'original': 'Upload fehlgeschlagen!'})
        return self.cleaned_data


class AttachmentAdmin(DisplayImageWidgetAdmin):
    form = AttachmentModelForm
    image_display_fields = ['processed']
    search_fields = ['title']
    ordering = ['-upload_date']
    date_hierarchy = 'upload_date'
    list_display = (
        'title',
        'extension',
        'upload_date',
    )

    def extension(self, obj):
        return splitext(str(obj.original))[-1]
    extension.short_description = 'Typ'


class HasAttachmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['attachment']


class HasAttachmentAdminInline(admin.StackedInline):
    autocomplete_fields = ['attachment']


class HasAttachmentModelForm(forms.ModelForm):
    attachment_preview = forms.FileField(
        label='Vorschau',
        widget=AdminDisplayImageWidget(),
        required=False,
        help_text='Wird erst nach dem Speichern der Meldung aktualisiert.'
    )

    def get_initial_for_field(self, field, field_name):
        if field_name == 'attachment_preview':
            try:
                return self.instance.attachment.processed
            except AttributeError:
                return None
        elif field_name == 'attachment':
            field.widget.can_delete_related = False

        return super().get_initial_for_field(field, field_name)


admin.site.register(Attachment, AttachmentAdmin)
