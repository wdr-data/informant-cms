from django.contrib import admin, messages
import logging

IMAGE_PROCESSING_FAILED = 'Automatische Bildverarbeitung fehlgeschlagen'


class AttachmentAdmin(admin.ModelAdmin):

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

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        for form_ in formset.forms:
            if 'media_original' in form_.changed_data or 'media_note' in form_.changed_data:
                try:
                    form_.instance.update_attachment()
                    form.changed_data = ['media']
                    super().save_formset(request, form, formset, change)

                except:
                    logging.exception('%s', form_.instance.media_original)
                    messages.error(request, f'{IMAGE_PROCESSING_FAILED}: '
                                            f'{form_.instance.media_original}')
