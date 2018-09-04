from django import forms

from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea

from .attachment import DisplayImageWidgetStackedInline


class QuizModelForm(forms.ModelForm):
    quiz_option= forms.CharField(
        required=False, label="Quiz Option", widget=EmojiPickerTextInput, max_length=20)
    quiz_text = forms.CharField(
        required=True, label="Quiz Antwort", widget=EmojiPickerTextarea, max_length=640)


class QuizAdminInline(DisplayImageWidgetStackedInline):
    image_display_fields = ['media']
    extra = 1
