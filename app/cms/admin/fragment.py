from django import forms

from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea

from .attachment import DisplayImageWidgetStackedInline


class FragmentModelForm(forms.ModelForm):
    question = forms.CharField(
        required=False, label="Frage", widget=EmojiPickerTextInput, max_length=20)
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextarea, max_length=2000)


class FragmentAdminInline(DisplayImageWidgetStackedInline):
    image_display_fields = ['media']
    extra = 1
