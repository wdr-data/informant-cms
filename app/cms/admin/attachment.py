import asyncio
import logging
import os
import requests
from posixpath import join as urljoin

import httpx
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from raven.contrib.django.raven_compat.models import client

ATTACHMENT_TRIGGER_URLS = [
    urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'attachment'),
]

if 'BOT_SERVICE_ENDPOINT_OLD' in os.environ:
    ATTACHMENT_TRIGGER_URLS.append(urljoin(os.environ['BOT_SERVICE_ENDPOINT_OLD'], 'attachment'))

IMAGE_PROCESSING_FAILED = 'Automatische Bildverarbeitung fehlgeschlagen'


async def _trigger_attachments(url):
    async with httpx.Client() as client:
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
            client.captureException(result)

    return not failed and all(result.status_code == 200 for results in results)


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
    image_display_fields = ['media']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if ('media_original' in form.changed_data
                or 'media_note' in form.changed_data
                or obj.media_original and not obj.media):
            try:
                path, url = obj.process_attachment()

            except:
                logging.exception('%s', obj.media_original)
                messages.error(request, f'{IMAGE_PROCESSING_FAILED}: {obj.media_original}')

            else:
                if path is None:
                    obj.media = None
                    form.changed_data = ['media']
                    super().save_model(request, obj, form, change)
                    return

                success = trigger_attachments(url)

                if success:
                    messages.success(
                        request, f'Anhang {obj.media_original} wurde zu Facebook hochgeladen 👌')

                    obj.media = path
                    form.changed_data = ['media']
                    super().save_model(request, obj, form, change)

                else:
                    messages.error(
                        request,
                        f'Anhang {obj.media_original} konnte nicht zu Facebook hochgeladen werden')

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        for form_ in formset.forms:
            if 'media_original' in form_.changed_data or 'media_note' in form_.changed_data:
                try:
                    path, url = form_.instance.process_attachment()

                except:
                    logging.exception('%s', form_.instance.media_original)
                    messages.error(request, f'{IMAGE_PROCESSING_FAILED}: '
                                            f'{form_.instance.media_original}')

                else:
                    if path is None:
                        form_.instance.media = None
                        form_.changed_data = ['media']
                        super().save_formset(request, form, formset, change)
                        return

                    success = trigger_attachments(url)

                    if success:
                        messages.success(
                            request,
                            f'Anhang {form_.instance.media_original} wurde zu Facebook '
                            f'hochgeladen 👌')

                        form_.instance.media = path
                        form_.changed_data = ['media']
                        super().save_formset(request, form, formset, change)

                    else:
                        messages.error(
                            request,
                            f'Anhang {form_.instance.media_original} konnte nicht zu Facebook '
                            f'hochgeladen werden')
