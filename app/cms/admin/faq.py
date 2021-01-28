from django.contrib import admin
from django import forms
from emoji_picker.widgets import EmojiPickerTextareaAdmin

from ..models.faq import FAQ, FAQFragment
from .attachment import HasAttachmentAdmin, HasAttachmentModelForm
from .fragment import FragmentModelForm, FragmentAdminInline


class FAQFragmentModelForm(FragmentModelForm):
    class Meta:
        model = FAQFragment
        fields = ["attachment", "attachment_preview", "text"]


class FAQFragmentAdminInline(FragmentAdminInline):
    model = FAQFragment
    form = FAQFragmentModelForm
    fields = ["attachment", "attachment_preview", "text"]
    fk_name = "faq"


class FAQModelForm(HasAttachmentModelForm):
    text = forms.CharField(
        required=True, label="Text", widget=EmojiPickerTextareaAdmin, max_length=550
    )

    slug = forms.CharField(
        label="Slug",
        help_text="Wird automatisch ausgefüllt",
        disabled=True,
        required=False,
    )
    description = forms.CharField(
        required=False,
        label="Beschreibung",
        max_length=400,
        widget=EmojiPickerTextareaAdmin,
        help_text="Wo wird der Text im Bot eingesetzt? Wie kann ich die Antwort triggern?",
    )

    class Meta:
        model = FAQ
        fields = [
            "name",
            "slug",
            "description",
            "attachment",
            "attachment_preview",
            "text",
        ]


class FAQAdmin(HasAttachmentAdmin):
    form = FAQModelForm
    ordering = ("name",)
    search_fields = ["name", "slug", "description"]
    fieldsets = [
        (None, {"fields": (("name", "slug"), "description")}),
        ("FAQ-Antwort", {"fields": ("attachment", "attachment_preview", "text")}),
    ]
    list_display = ("name", "slug", "description")
    inlines = (FAQFragmentAdminInline,)


# Register your models here.
admin.site.register(FAQ, FAQAdmin)
