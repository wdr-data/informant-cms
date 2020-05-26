from django import forms
from django.contrib import admin

from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin

from .attachment import DisplayImageWidgetStackedInline, HasAttachmentModelForm, HasAttachmentAdminInline


class FragmentModelForm(HasAttachmentModelForm):
    question = forms.CharField(
        required=False,
        label="Frage",
        widget=EmojiPickerTextInputAdmin,
        max_length=20,
        help_text='Nicht ausfüllen einer Frage führt zum direkten Senden des Fragments.')
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextareaAdmin, max_length=550)


class FragmentAdminInline(HasAttachmentAdminInline):
    extra = 1
