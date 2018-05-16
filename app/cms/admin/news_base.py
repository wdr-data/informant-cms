from django import forms
from tags_input import admin as tags_input_admin
from emoji_picker.widgets import EmojiPickerTextarea

from .attachment import AttachmentAdmin


class NewsBaseModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Intro-Text", widget=EmojiPickerTextarea, max_length=640)


class NewsBaseAdmin(tags_input_admin.TagsInputAdmin, AttachmentAdmin):
    tag_fields = ['tags']
