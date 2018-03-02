import os

from django.contrib import admin, messages
from django import forms
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
import requests

from ..models.push import Push
from .attachment import AttachmentAdmin

PUSH_TRIGGER_URL = os.environ['PUSH_TRIGGER_URL']


class PushModelForm(forms.ModelForm):
    intro = forms.CharField(
        required=True, label="Intro-Text", widget=forms.Textarea, max_length=640)
    outro = forms.CharField(
        required=True, label="Outro-Text", widget=forms.Textarea, max_length=640)

    delivered = forms.BooleanField(
        label='Versendet', help_text="Wurde dieser Push bereits versendet?", disabled=True,
        required=False)

    class Meta:
        model = Push
        fields = ('pub_date', 'timing', 'headline', 'intro', 'reports',
                  'outro', 'media', 'media_original', 'media_note',
                  'published', 'delivered')


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
        super().save_model(request, obj, form, change)

        try:
            if obj.timing == Push.Timing.BREAKING.value and obj.published and not obj.delivered:
                r = requests.get(
                    url=PUSH_TRIGGER_URL,
                    params={'timing': Push.Timing.BREAKING.value}
                )

                result = r.json()

                if result.get('success', False):
                    obj.delivered = True
                    form.changed_data = ['delivered']
                    super().save_model(request, obj, form, change)

                    messages.success(request, result.get('message', 'Push wurde gesendet'))

                else:
                    messages.error(
                        request, result.get('message', 'Push konnte nicht gesendet werden'))

        except Exception as e:
            messages.error(request, str(e))


# Register your models here.
admin.site.register(Push, PushAdmin)
