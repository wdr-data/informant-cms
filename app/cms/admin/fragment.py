from django import forms

from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin

from .attachment import DisplayImageWidgetStackedInline


class FragmentModelForm(forms.ModelForm):
    question = forms.CharField(
        required=False, label="Frage", widget=EmojiPickerTextInputAdmin, max_length=20)
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextareaAdmin, max_length=2000)


class FragmentAdminInline(DisplayImageWidgetStackedInline):
    image_display_fields = ['media']
    extra = 1
