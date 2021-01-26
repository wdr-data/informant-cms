from django.db import models
from datetime import date
from sortedm2m.fields import SortedManyToManyField

from .attachment import HasAttachment


class Promo(HasAttachment):
    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promo"

    text = models.CharField("Promo-Text", max_length=500, null=False)

    link_name = models.CharField(
        "Link-Button-Text", max_length=17, null=True, blank=True
    )

    link = models.URLField(
        "Link",
        blank=True,
        null=True,
        max_length=500,
        default=None,
        help_text="Der Link wird am Ende am Ende des Promo-Text als Button angehangen. "
        'Der Button-Text lautet: "🔗 {Link-Button-Text}".'
        "Damit bietet das Outro u.a. die Möglichkeit der Cross-Promo von WDR-Inhalten.",
    )


class PushCompact(HasAttachment):
    """
    Pushes fassen Meldungen zusammen. Diese Meldungen werden zum jeweils festgelegten Zeitpunkt
    an alle Abonnenten versandt.
    """

    class Meta:
        verbose_name = "Push"
        verbose_name_plural = "Morgen-Pushes"

    class DeliveryStatus(models.TextChoices):
        NOT_SENT = "not_sent", "nicht gesendet"
        SENDING = "sending", "wird gesendet"
        SENT = "sent", "gesendet"

    pub_date = models.DateField("Push Datum", default=date.today)

    published = models.BooleanField(
        "Freigegeben",
        null=False,
        default=False,
        help_text="Solange dieser Haken nicht gesetzt ist, wird dieser Push nicht versendet, "
        "auch wenn der konfigurierte Zeitpunkt erreicht wird.",
    )

    intro = models.CharField("Intro-Text", max_length=250, null=False)

    outro = models.CharField(
        "Outro-Text",
        max_length=150,
        null=False,
        help_text="Der Outro-Text schließt den Push ab. Die 👋  wird automatisch hinzugefügt.",
    )

    delivered_fb = models.CharField(
        "Facebook",
        null=False,
        blank=False,
        max_length=20,
        choices=[
            (DeliveryStatus.NOT_SENT.value, "nicht gesendet"),
            (DeliveryStatus.SENDING.value, "wird gesendet"),
            (DeliveryStatus.SENT.value, "gesendet"),
        ],
        default=DeliveryStatus.NOT_SENT.value,
    )

    delivered_date_fb = models.DateTimeField("Versand-Datum Facebook", null=True)

    delivered_tg = models.CharField(
        "Telegram",
        null=False,
        blank=False,
        max_length=20,
        choices=[
            (DeliveryStatus.NOT_SENT.value, "nicht gesendet"),
            (DeliveryStatus.SENDING.value, "wird gesendet"),
            (DeliveryStatus.SENT.value, "gesendet"),
        ],
        default=DeliveryStatus.NOT_SENT.value,
    )

    delivered_date_tg = models.DateTimeField("Versand-Datum Telegram", null=True)

    promo = models.OneToOneField(Promo, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"""☕ Morgen - {
            self.pub_date.strftime('%d.%m.%Y')
        }"""

    @classmethod
    def last(
        cls,
        *,
        count=1,
        offset=0,
        only_published=True,
        delivered=False,
        by_date=True,
        breaking=True,
    ):
        pushes = cls.objects.all()

        if only_published:
            pushes = pushes.filter(published=True)

        if not breaking:
            pushes = pushes.exclude(timing="breaking")

        if not delivered:
            pushes = pushes.filter(
                delivered_fb=PushCompact.DeliveryStatus.NOT_SENT.value,
                delivered_tg=PushCompact.DeliveryStatus.NOT_SENT.value,
            )

        if by_date:
            pushes = pushes.order_by("-pub_date", "timing")
        else:
            pushes = pushes.order_by("-id")

        return pushes[offset:count]


class Teaser(models.Model):
    class Meta:
        verbose_name = "Meldung"
        verbose_name_plural = "Meldungen"

    headline = models.CharField(
        "Erste Zeile",
        max_length=100,
        null=False,
        help_text="Die erste Zeile wird bei Telegram gefettet.",
    )

    summary = models.CharField(
        "Text",
        max_length=400,
        null=True,
        blank=True,
        help_text="Dieser Text wird ergänzen gespielt.",
    )

    short_headline = models.CharField(
        "Telegram-Link-Text",
        max_length=30,
        null=False,
        help_text="Hinter diesem Schlagwort wird in TG der Deeplink als Hyperlink gesetzt.",
    )

    link = models.URLField(
        "Kurz-Link",
        blank=True,
        null=True,
        max_length=100,
        default=None,
        help_text="Der Kurz-Link wird nach dem Meldungstext ausgespielt."
        "Bei Telegram als Hyperlink hin dem Telegram-Link-Text. Bei Facebook direkt als Kurz-Link.",
    )

    push = models.ForeignKey(
        PushCompact,
        on_delete=models.CASCADE,
        related_name="teasers",
        related_query_name="teaser",
    )

    push = models.ForeignKey(
        PushCompact,
        on_delete=models.CASCADE,
        related_name="teasers",
        related_query_name="teaser",
    )
