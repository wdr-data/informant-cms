from django.contrib import admin
from django import forms
from tags_input import admin as tags_input_admin

from ..models.report import Report, ReportFragment
from .attachment import AttachmentAdmin, DisplayImageWidgetTabularInline, DisplayImageWidgetStackedInline


class ReportFragmentModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Text", widget=forms.Textarea, max_length=640)

    class Meta:
        model = ReportFragment
        fields = ['question', 'text', 'media', 'media_original', 'media_note']


class ReportFragmentAdmin(admin.ModelAdmin):
    form = ReportFragmentModelForm


class ReportFragmentAdminInline(DisplayImageWidgetTabularInline):
    image_display_fields = ['media']
    model = ReportFragment
    form = ReportFragmentModelForm

    extra = 1


class ReportModelForm(forms.ModelForm):
    text = forms.CharField(
        required=True, label="Intro-Text", widget=forms.Textarea, max_length=640)

    delivered = forms.BooleanField(
        label='Versendet',
        help_text="Wurde diese Meldung bereits in einem Highlights-Push vom Bot versendet?",
        disabled=True,
        required=False)

    class Meta:
        model = Report
        fields = ['headline', "genres", 'topic', 'tags', 'text', 'media', 'media_original',
                  'media_note', 'created', 'published', 'delivered']


class ReportAdmin(tags_input_admin.TagsInputAdmin, AttachmentAdmin):
    form = ReportModelForm
    date_hierarchy = 'created'
    list_filter = ['published']
    search_fields = ['headline']
    list_display = ('headline', 'created', 'published')
    inlines = (ReportFragmentAdminInline, )
    tag_fields = ['tags']


# Register your models here.
admin.site.register(Report, ReportAdmin)

