from django.contrib import admin
from django import forms
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple

from ..models.push import Push


class PushModelForm(forms.ModelForm):
    intro = forms.CharField(
        required=True, label="Intro-Text", widget=forms.Textarea, max_length=640)
    outro = forms.CharField(
        required=True, label="Outro-Text", widget=forms.Textarea, max_length=640)

    class Meta:
        model = Push
        fields = '__all__'


class PushAdmin(admin.ModelAdmin):
    form = PushModelForm
    date_hierarchy = 'pub_date'
    list_filter = ['published']
    search_fields = ['headline']
    list_display = ('headline', 'pub_date', 'published', 'delivered')

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ('reports', ):
            kwargs['widget'] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    class Media:
        js = (
            'cms/js/script.js',
        )

# Register your models here.
admin.site.register(Push, PushAdmin)
