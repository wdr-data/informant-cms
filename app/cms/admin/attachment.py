import asyncio
import logging
import os
import requests
from posixpath import join as urljoin

import httpx
from django import forms
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


class AttachmentAdmin(DisplayImageWidgetAdmin):
    image_display_fields = ['processed']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if ('original' in form.changed_data
                or 'credit' in form.changed_data
                or obj.original and not obj.processed):
            try:
                path, url = obj.process_attachment()

            except:
                logging.exception('%s', obj.original)
                messages.error(request, f'{IMAGE_PROCESSING_FAILED}: {obj.original}')

            else:
                if path is None:
                    obj.processed = None
                    form.changed_data = ['processed']
                    super().save_model(request, obj, form, change)
                    return

                success = trigger_attachments(url)

                if success:
                    messages.success(
                        request, f'Anhang {obj.original} wurde zu Facebook hochgeladen 👌')

                    obj.processed = path
                    form.changed_data = ['processed']
                    super().save_model(request, obj, form, change)

                else:
                    messages.error(
                        request,
                        f'Anhang {obj.original} konnte nicht zu Facebook hochgeladen werden')

class HasAttachmentAdmin(admin.ModelAdmin):
    pass

class HasAttachmentModelForm(forms.ModelForm):
    pass

admin.site.register(Attachment, AttachmentAdmin)
