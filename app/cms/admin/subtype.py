from django.contrib import admin
from django import forms
from emoji_picker.widgets import EmojiPickerTextInputAdmin

from ..models.subtype import Subtype

class SubtypeModelForm(forms.ModelForm):
    class Meta:
        model = Subtype
        fields = "__all__"

    emoji = forms.CharField(label='Emoji', widget=EmojiPickerTextInputAdmin, max_length=3)

class SubtypeAdmin(admin.ModelAdmin):
    form = SubtypeModelForm

# Register your model here
admin.site.register(Subtype, SubtypeAdmin)
