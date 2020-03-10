from django import forms
from django.contrib import admin

from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin

from .attachment import DisplayImageWidgetStackedInline, HasAttachmentModelForm


class FragmentModelForm(HasAttachmentModelForm):
    question = forms.CharField(
        required=False, label="Frage", widget=EmojiPickerTextInputAdmin, max_length=20)
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextareaAdmin, max_length=950)


class FragmentAdminInline(admin.StackedInline):
    extra = 1
