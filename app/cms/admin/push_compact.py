from posixpath import join as urljoin
from datetime import date, time, datetime

from django.contrib import admin, messages
from django import forms
from django.utils import dateformat
from emoji_picker.widgets import EmojiPickerTextareaAdmin, EmojiPickerTextInputAdmin
import requests
from django.core.exceptions import ValidationError
from admin_object_actions.admin import ModelAdminObjectActionsMixin
from admin_object_actions.forms import AdminObjectActionForm
from crum import get_current_request
import pytz
from adminsortable2.admin import CustomInlineFormSet, SortableInlineAdminMixin

from ..models.push_compact import PushCompact, Promo, Teaser
from .attachment import (
    HasAttachmentAdmin,
    HasAttachmentAdminInline,
    HasAttachmentModelForm,
)
from ..env import (
    PUSH_TRIGGER_URLS,
    BOT_SERVICE_ENDPOINT_FB,
    BOT_SERVICE_ENDPOINT_TG,
    MANUAL_PUSH_GROUP,
)


MIN_TEASERS = 3
MAX_TEASERS = 3


class PushCompactModelForm(HasAttachmentModelForm):
    class Meta:
        model = PushCompact
        exclude = ()

    intro = forms.CharField(
        required=(not PushCompact.intro.field.null),
        label="Text",
        widget=EmojiPickerTextareaAdmin,
        max_length=PushCompact.intro.field.max_length,
    )
    outro = forms.CharField(
        required=(not PushCompact.outro.field.null),
        label="Text",
        widget=EmojiPickerTextareaAdmin,
        max_length=PushCompact.outro.field.max_length,
    )


class PromoModelForm(HasAttachmentModelForm):
    class Meta:
        model = Promo
        exclude = ()

    text = forms.CharField(
        required=True,
        label="Text",
        widget=EmojiPickerTextareaAdmin,
        max_length=Promo.text.field.max_length,
        help_text=Promo.text.field.help_text,
    )


class PromoAdminInline(SortableInlineAdminMixin, HasAttachmentAdminInline):
    model = Promo
    form = PromoModelForm
    fields = [
        "short_headline",
        "attachment",
        "attachment_preview",
        "text",
        "link_name",
        "link",
    ]
    extra = 0
    min_num = 0
    max_num = 2


class TeaserModelForm(forms.ModelForm):
    class Meta:
        model = Teaser
        exclude = ()

    headline = forms.CharField(
        label="Erste Zeile",
        widget=EmojiPickerTextInputAdmin,
        max_length=Teaser.headline.field.max_length,
        help_text="Bei Telegram wird die erste Zeile gefettet. Bei Facebook ist die erste Zeile abgesetzt. In beiden Fällen wird automatisch ein ➡️ vorangestellt.",
    )

    text = forms.CharField(
        label="Text",
        widget=EmojiPickerTextareaAdmin,
        max_length=Teaser.text.field.max_length,
        help_text="Die erste Zeile in Kombination mit dem Text sollen als Fließtext zu lesen sein.",
    )

    def clean(self):
        if self.cleaned_data.get("link") and not self.cleaned_data.get("link_name"):
            raise ValidationError(
                {
                    "link_name": "Wenn der Link gesetzt ist, muss auch ein Link-Text gesetzt sein."
                }
            )


class TeaserFormSet(CustomInlineFormSet):
    def clean(self) -> None:
        published = self.instance.published or "_publish-save" in self.data
        total_forms = (
            len(self.initial_forms) + len(self.extra_forms) - len(self.deleted_forms)
        )

        if published and total_forms < MIN_TEASERS:
            raise ValidationError(
                f"Ein freigegebener Push muss mindestens {MIN_TEASERS} Meldungen haben."
            )

        return super().clean()


class TeaserAdminInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Teaser
    form = TeaserModelForm
    formset = TeaserFormSet
    extra = 0
    min_num = 0
    max_num = MAX_TEASERS


class SendManualForm(AdminObjectActionForm):

    confirm = forms.BooleanField(
        required=True,
        help_text="""Nur manuell senden, falls ein Push nicht automatisch versendet wurde, weil er z. B. nicht rechtzeitig freigegeben wurde.
        Falls in einem Kanal bereits gesendet wurde, wird in diesem Kanal nicht noch einmal versendet.""",
        label="Ja, ich möchte wirklich den Push manuell versenden",
    )

    class Meta:
        model = PushCompact
        fields = ()

    def do_object_action(self):
        failed = []
        for service, push_trigger_url in PUSH_TRIGGER_URLS.items():
            if (
                PushCompact.DeliveryStatus(
                    getattr(self.instance, f"delivered_{service}")
                )
                is not PushCompact.DeliveryStatus.NOT_SENT
            ):
                continue

            r = requests.post(
                url=push_trigger_url,
                json={
                    "push": self.instance.id,
                    "options": {
                        "manual": True,
                    },
                },
            )

            if not r.ok:
                failed.append(service.upper())

        if failed:
            raise Exception(
                f'Manuelles Senden für mindestens einen Bot ist fehlgeschlagen ({", ".join(failed)})'
            )


class PushCompactAdmin(ModelAdminObjectActionsMixin, HasAttachmentAdmin):
    form = PushCompactModelForm
    change_form_template = "admin/cms/change_form_push_compact.html"

    inlines = [
        TeaserAdminInline,
        PromoAdminInline,
    ]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "display_object_actions_detail",
                    "published",
                    ("pub_date",),
                )
            },
        ),
        (
            "Push-Intro",
            {
                "fields": (
                    "attachment",
                    "attachment_preview",
                    "intro",
                )
            },
        ),
        ("Push-Outro", {"fields": ("outro",)}),
    ]

    date_hierarchy = "pub_date"
    list_filter = ["published"]
    list_display = (
        "published",
        "weekday",
        "pub_date",
        "send_status",
        "display_object_actions_list",
    )
    readonly_fields = ("display_object_actions_detail",)
    list_display_links = ("pub_date", "weekday")
    ordering = ("-pub_date",)

    def display_object_actions_list(self, obj=None):
        return self.display_object_actions(obj, list_only=True)

    display_object_actions_list.short_description = "Aktionen"

    def display_object_actions_detail(self, obj=None):
        return self.display_object_actions(obj, detail_only=True)

    display_object_actions_detail.short_description = "Aktionen"

    object_actions = [
        {
            "slug": "preview-push",
            "verbose_name": "Testen",
            "verbose_name_past": "tested",
            "form_method": "GET",
            "function": "preview",
        },
        {
            "slug": "manual-push",
            "verbose_name": "Manuell senden",
            "verbose_name_past": "sent",
            "form_class": SendManualForm,
            "permission": "send_manual",
        },
    ]

    def weekday(self, obj):
        display = dateformat.format(obj.pub_date, "l")
        return display

    weekday.short_description = "Wochentag"

    def send_status(self, obj):

        if (
            PushCompact.DeliveryStatus(obj.delivered_fb)
            == PushCompact.DeliveryStatus.NOT_SENT
        ):
            display = "FB: ❌"
        elif (
            PushCompact.DeliveryStatus(obj.delivered_fb)
            == PushCompact.DeliveryStatus.SENDING
        ):
            display = "FB: 💬"
        else:
            display = "FB: ✅"

        if (
            PushCompact.DeliveryStatus(obj.delivered_tg)
            == PushCompact.DeliveryStatus.NOT_SENT
        ):
            display += "  TG: ❌️"
        elif (
            PushCompact.DeliveryStatus(obj.delivered_tg)
            == PushCompact.DeliveryStatus.SENDING
        ):
            display += "  TG: 💬"
        else:
            display += "  TG: ✅"

        return display

    send_status.short_description = "Sende-Status"

    def preview(self, obj, form):
        request = get_current_request()
        profile = request.user.profile

        if not profile:
            error_message = "Bitte trage deine Nutzer-ID für Facebook und/oder Telegram in deinem Profil ein."
            raise Exception(error_message)

        failed = False

        if profile.psid:
            r = requests.post(
                url=urljoin(BOT_SERVICE_ENDPOINT_FB, "push"),
                json={
                    "push": obj.id,
                    "options": {
                        "preview": profile.psid,
                    },
                },
            )

            if not r.ok:
                messages.error(request, "Testen bei Facebook ist fehlgeschlagen.")
                failed = True

        else:
            messages.warning(
                request,
                "Bitte trage deine Facebook-ID in deinem Profil ein, um in Facebook testen zu können.",
            )

        if profile.tgid:
            r = requests.post(
                url=urljoin(BOT_SERVICE_ENDPOINT_TG, "push"),
                json={
                    "push": obj.id,
                    "options": {
                        "preview": profile.tgid,
                    },
                },
            )

            if not r.ok:
                messages.error(request, "Testen bei Telegram ist fehlgeschlagen.")
                failed = True

        else:
            messages.warning(
                request,
                "Bitte trage deine Telegram-ID in deinem Profil ein, um in Telegram testen zu können.",
            )

        if failed:
            raise Exception("Es ist ein Fehler aufgetreten.")

    def has_send_manual_permission(self, request, obj=None):
        return (
            obj.published
            and (
                PushCompact.DeliveryStatus(obj.delivered_fb)
                is PushCompact.DeliveryStatus.NOT_SENT
                or PushCompact.DeliveryStatus(obj.delivered_tg)
                is PushCompact.DeliveryStatus.NOT_SENT
            )
            and obj.pub_date == date.today()
            and (
                request.user.is_superuser
                or any(
                    group.name == MANUAL_PUSH_GROUP
                    for group in request.user.groups.all()
                )
            )
        )

    def save_model(self, request, obj, form, change):
        local_time = datetime.now(tz=pytz.timezone("Europe/Berlin"))
        if obj.pub_date < local_time.date():
            messages.warning(
                request,
                "Das Push-Datum für diesen Push liegt in der Vergangenheit. "
                "Dieser Push wird daher nicht gesendet. Bitte Datum prüfen!",
            )
        elif obj.pub_date == local_time.date() and local_time.time() > time(10, 00):
            messages.warning(
                request,
                "Der Push hat das Datum von heute, ist aber ein Morgen-Push. "
                "Dieser Push wird daher nicht gesendet. Bitte Datum prüfen!",
            )

        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_publish-save" in request.POST:
            obj.published = True
            obj.save()
            self.message_user(
                request,
                f"Der Push ist freigegeben.",
            )
        return super().response_change(request, obj)


# Register your models here.
admin.site.register(PushCompact, PushCompactAdmin)
