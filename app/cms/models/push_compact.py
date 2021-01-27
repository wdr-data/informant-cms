from datetime import date

from django.db import models

from .attachment import HasAttachment


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

    pub_date = models.DateField(
        "Push Datum",
        default=date.today,
    )

    published = models.BooleanField(
        "Freigegeben",
        null=False,
        default=False,
        help_text="Solange dieser Haken nicht gesetzt ist, wird dieser Push nicht versendet, "
        "auch wenn der konfigurierte Zeitpunkt erreicht wird.",
    )

    intro = models.CharField(
        "Intro-Text",
        max_length=250,
        null=False,
    )

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

    delivered_date_fb = models.DateTimeField(
        "Versand-Datum Facebook",
        null=True,
    )

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

    delivered_date_tg = models.DateTimeField(
        "Versand-Datum Telegram",
        null=True,
    )

    def __str__(self):
        return f"""☕ Morgen - {
            self.pub_date.strftime('%d.%m.%Y')
        }"""


class Teaser(models.Model):
    class Meta:
        verbose_name = "Meldung"
        verbose_name_plural = "Meldungen"
        ordering = ["ordering"]

    headline = models.CharField(
        "Erste Zeile",
        max_length=100,
        null=False,
        help_text="Die erste Zeile wird bei Telegram gefettet.",
    )

    text = models.CharField(
        "Text",
        max_length=400,
        blank=True,
        help_text="Dieser Text wird ergänzen gespielt.",
    )

    link_name = models.CharField(
        "Telegram-Link-Text",
        max_length=30,
        blank=True,
        help_text="Hinter diesem Schlagwort wird in TG der Deeplink als Hyperlink gesetzt.",
    )

    link = models.URLField(
        "Kurz-Link",
        blank=True,
        max_length=100,
        default=None,
        help_text="Der Kurz-Link wird nach dem Meldungstext ausgespielt. "
        "Bei Telegram als Hyperlink hin dem Telegram-Link-Text. Bei Facebook direkt als Kurz-Link.",
    )

    push = models.ForeignKey(
        PushCompact,
        on_delete=models.CASCADE,
        related_name="teasers",
        related_query_name="teaser",
    )

    ordering = models.PositiveSmallIntegerField(
        "Sortierung",
        default=0,
    )

    def __str__(self):
        return self.headline


class Promo(HasAttachment):
    class Meta:
        verbose_name = "Promo"
        verbose_name_plural = "Promos"
        ordering = ["ordering"]

    short_headline = models.CharField(
        "Button-Text",
        max_length=17,
        help_text="Titel des Buttons, der zu dieser Promo führt.",
    )

    text = models.CharField(
        "Promo-Text",
        max_length=500,
        null=False,
    )

    link_name = models.CharField(
        "Link-Button-Text",
        max_length=17,
        blank=True,
        help_text="Optional. Wenn kein Link-Button-Text gesetzt ist, wird der Button-Text automatisch gesetzt.",
    )

    link = models.URLField(
        "Link",
        blank=True,
        max_length=500,
        default=None,
        help_text="Der Link wird am Ende am Ende des Promo-Text als Button angehangen.",
    )

    push = models.ForeignKey(
        PushCompact,
        on_delete=models.CASCADE,
        related_name="promos",
        related_query_name="promo",
    )

    ordering = models.PositiveSmallIntegerField(
        "Sortierung",
        default=0,
    )

    def __str__(self):
        return self.short_headline
