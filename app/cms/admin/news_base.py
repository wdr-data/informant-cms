from django import forms
from tags_input import admin as tags_input_admin
from emoji_picker.widgets import EmojiPickerTextareaAdmin

from .attachment import HasAttachmentAdmin, HasAttachmentModelForm


class NewsBaseModelForm(HasAttachmentModelForm):
    text = forms.CharField(
        required=True,
        label="Facebook-Text",
        widget=EmojiPickerTextareaAdmin,
        max_length=950,
    )


class NewsBaseAdmin(tags_input_admin.TagsInputAdmin, HasAttachmentAdmin):
    tag_fields = ["tags"]
