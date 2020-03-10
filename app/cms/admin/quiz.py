from django import forms
from django.contrib import admin

from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin

from .attachment import HasAttachmentModelForm


class QuizModelForm(HasAttachmentModelForm):
    correct_option = forms.BooleanField(required=False, label='Richtige Antwort',
        help_text='Setze hier einen Haken, wenn diese Antwort-Option die richtige ist.')
    quiz_option = forms.CharField(
        required=True, label='Quiz Option', widget=EmojiPickerTextInputAdmin, max_length=20,
        help_text='Trage hier den Button-Text für eine Antwortmöglichkeit ein. '
                  'Um ein Quiz zu erstellen müssen mindestens 2, maximal 3 Buttons gegeben sein.')
    quiz_text = forms.CharField(
        required=True, label='Quiz Antwort', widget=EmojiPickerTextareaAdmin, max_length=950,
        help_text='Hier kannst du einen individuellen Text für diese Antwortmöglichkeit eintragen')


class QuizAdminInline(admin.StackedInline):
    extra = 0
