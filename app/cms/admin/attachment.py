import logging
import os
import requests
from posixpath import join as urljoin

from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

ATTACHMENT_TRIGGER_URL = urljoin(os.environ['BOT_SERVICE_ENDPOINT'], 'attachment')
IMAGE_PROCESSING_FAILED = 'Automatische Bildverarbeitung fehlgeschlagen'


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

        if 'media_original' in form.changed_data or 'media_note' in form.changed_data:
            try:
                obj.update_attachment()
                form.changed_data = ['media']
                super().save_model(request, obj, form, change)

            except:
                logging.exception('%s', obj.media_original)
                messages.error(request, f'{IMAGE_PROCESSING_FAILED}: {obj.media_original}')

            if obj.media:
                r = requests.post(
                    ATTACHMENT_TRIGGER_URL,
                    json={'url': obj.media.url}
                )

                if r.status_code == 200:
                    messages.success(
                        request, f'Anhang {obj.media_original} wurde zu Facebook hochgeladen 👌')

                else:
                    messages.error(
                        request,
                        f'Anhang {obj.media_original} konnte nicht zu Facebook hochgeladen werden')

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        for form_ in formset.forms:
            if 'media_original' in form_.changed_data or 'media_note' in form_.changed_data:
                try:
                    form_.instance.update_attachment()
                    form_.changed_data = ['media']
                    super().save_formset(request, form, formset, change)

                except:
                    logging.exception('%s', form_.instance.media_original)
                    messages.error(request, f'{IMAGE_PROCESSING_FAILED}: '
                                            f'{form_.instance.media_original}')

                if form_.instance.media:
                    r = requests.post(
                        ATTACHMENT_TRIGGER_URL,
                        json={'url': form_.instance.media.url}
                    )

                    if r.status_code == 200:
                        messages.success(
                            request,
                            f'Anhang {form_.instance.media_original} wurde zu Facebook '
                            f'hochgeladen 👌')

                    else:
                        messages.error(
                            request,
                            f'Anhang {form_.instance.media_original} konnte nicht zu Facebook '
                            f'hochgeladen werden')
