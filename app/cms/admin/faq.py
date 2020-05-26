from django.contrib import admin
from django import forms
from emoji_picker.widgets import EmojiPickerTextareaAdmin

from ..models.faq import FAQ, FAQFragment
from .attachment import HasAttachmentAdmin, HasAttachmentModelForm
from .fragment import FragmentModelForm, FragmentAdminInline


class FAQFragmentModelForm(FragmentModelForm):

    class Meta:
        model = FAQFragment
        fields = ['attachment', 'attachment_preview', 'text']


class FAQFragmentAdminInline(FragmentAdminInline):
    model = FAQFragment
    form = FAQFragmentModelForm
    fields = ['attachment', 'attachment_preview', 'text']
    fk_name = 'faq'


class FAQModelForm(HasAttachmentModelForm):
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextareaAdmin, max_length=550)

    slug = forms.CharField(
        label='Slug', help_text="Wird automatisch ausgefüllt", disabled=True,
        required=False)

    class Meta:
        model = FAQ
        fields = ['name', 'slug', 'attachment', 'attachment_preview', 'text']


class FAQAdmin(HasAttachmentAdmin):
    form = FAQModelForm
    ordering = ('name',)
    search_fields = ['name', 'slug']
    list_display = ('name', 'slug')
    inlines = (FAQFragmentAdminInline, )


# Register your models here.
admin.site.register(FAQ, FAQAdmin)
