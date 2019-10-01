from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from crum import get_current_request

from ..models.profile import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class ProfileModelForm(forms.ModelForm):
    def clean_user(self):
        request = get_current_request()
        if request.user.pk != self.cleaned_data['user'].pk and not request.user.is_superuser:
            raise forms.ValidationError('Du kannst nur dein eigenes Profil bearbeiten')
        return self.cleaned_data['user']


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileModelForm

    list_display = ('user', 'psid')
    fields = ('user', 'psid', )

    def get_changeform_initial_data(self, request):
        initial_data = super(ProfileAdmin, self).get_changeform_initial_data(request)
        if 'user' not in initial_data:
            initial_data['user'] = request.user.pk
        return initial_data


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
