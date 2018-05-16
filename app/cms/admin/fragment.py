from django import forms

from .attachment import DisplayImageWidgetStackedInline


class FragmentModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Text", widget=forms.Textarea, max_length=640)


class FragmentAdminInline(DisplayImageWidgetStackedInline):
    image_display_fields = ['media']
    extra = 1
