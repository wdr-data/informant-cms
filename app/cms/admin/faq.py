from django.contrib import admin
from django import forms
from emoji_picker.widgets import EmojiPickerTextarea

from ..models.faq import FAQ, FAQFragment
from .attachment import AttachmentAdmin
from .fragment import FragmentModelForm, FragmentAdminInline


class FAQFragmentModelForm(FragmentModelForm):

    class Meta:
        model = FAQFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_alt',
                  'media_note', 'link_faq']


class FAQFragmentAdminInline(FragmentAdminInline):
    model = FAQFragment
    form = FAQFragmentModelForm

    fk_name = 'faq'


class FAQModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextarea, max_length=640)

    slug = forms.CharField(
        label='Slug', help_text="Wird automatisch ausgefüllt", disabled=True,
        required=False)

    class Meta:
        model = FAQ
        fields = ['name', 'slug', 'text', 'media', 'media_original', 'media_alt',
                  'media_note']


class FAQAdmin(AttachmentAdmin):
    form = FAQModelForm
    search_fields = ['name', 'slug']
    list_display = ('name', 'slug')
    inlines = (FAQFragmentAdminInline, )


# Register your models here.
admin.site.register(FAQ, FAQAdmin)
