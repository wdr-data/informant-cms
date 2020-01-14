from django.contrib import admin
from django import forms
from emoji_picker.widgets import EmojiPickerTextareaAdmin

from ..models.faq import FAQ, FAQFragment
from .attachment import AttachmentAdmin
from .fragment import FragmentModelForm, FragmentAdminInline


class FAQFragmentModelForm(FragmentModelForm):

    class Meta:
        model = FAQFragment
        fields = ['media', 'media_original', 'media_alt', 'media_note', 'text']


class FAQFragmentAdminInline(FragmentAdminInline):
    model = FAQFragment
    form = FAQFragmentModelForm
    fields = ('media', 'media_original', 'media_alt', 'media_note', 'text',)
    fk_name = 'faq'


class FAQModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextareaAdmin, max_length=2000)

    slug = forms.CharField(
        label='Slug', help_text="Wird automatisch ausgefüllt", disabled=True,
        required=False)

    class Meta:
        model = FAQ
        fields = ['name', 'slug', 'media', 'media_original', 'media_alt',
                  'media_note', 'text']


class FAQAdmin(AttachmentAdmin):
    form = FAQModelForm
    ordering = ('name',)
    search_fields = ['name', 'slug']
    list_display = ('name', 'slug')
    inlines = (FAQFragmentAdminInline, )


# Register your models here.
admin.site.register(FAQ, FAQAdmin)
