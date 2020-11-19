from django.utils import timezone
from django.db import models
from s3direct.fields import S3DirectField

from .news_base import NewsBaseModel
from .fragment import Fragment
from .quiz import Quiz
from .subtype import Subtype


class Report(NewsBaseModel):
    """
    Meldungen sind themenbezogene, in sich abgeschlossene Nachrichten.</p><p>
    Sie können aus mehreren Fragmenten bestehen. Um von einem Fragment zum nächsten zu gelangen,
    muss der Nutzer mit dem Bot interagieren, indem er einen Button mit einer weiterführenden Frage
    o.ä. anklickt.
    """

    class Meta:
        verbose_name = "Meldung"
        verbose_name_plural = "Meldungen, Eilmeldungen und Abend-Content-Push"
        ordering = ["-created"]

    class Type(models.TextChoices):
        REGULAR = "regular", "📰 Reguläre Meldung"
        LAST = "last", "🎨 Letzte Meldung"
        BREAKING = "breaking", "🚨 Breaking"
        EVENING = "evening", "🌙 Abend-Push"
        NOTIFICATION = "notification", "📨 Benachrichtigung"

    class DeliveryStatus(models.TextChoices):
        NOT_SENT = "not_sent", "nicht gesendet"
        SENDING = "sending", "wird gesendet"
        SENT = "sent", "gesendet"

    type = models.CharField(
        "Meldungstyp",
        null=False,
        blank=False,
        max_length=20,
        choices=Type.choices,
        help_text='Wird dieser Wert auf "Breaking", "Abend-Push" oder "Benachrichtigung" '
        "gesetzt und die Meldung freigegeben, kann sie direkt versendet werden.",
        default=Type.REGULAR.value,
    )

    subtype = models.ForeignKey(
        Subtype,
        models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Subtyp",
        related_name="reports",
        related_query_name="report",
        help_text='Derzeit nur relevant für Meldungen vom Typ "🎨 Letzte Meldung".',
    )

    headline = models.CharField("Überschrift", max_length=200, null=False)

    summary = models.CharField(
        "Telegram-Text",
        max_length=900,
        null=True,
        blank=True,
        help_text="Dieser Text wird bei Telegram als Meldungstext zusammen mit der Überschrift ausgespielt.",
    )

    short_headline = models.CharField(
        "Link-/Button-Text",
        max_length=17,
        null=False,
        help_text="Hinter diesem Schlagwort wird in TG der Deeplink gesetzt. Außerdem ist dies der Text,"
        " der auf dem Auswahl-Button für diese Nachricht in FB angezeigt wird.",
    )

    created = models.DateTimeField("Erstellt", default=timezone.now)
    published_date = models.DateTimeField(
        "Veröffentlicht",
        null=True,
    )
    modified = models.DateTimeField(
        "Bearbeitet",
        null=False,
    )

    published = models.BooleanField(
        "Freigegeben",
        null=False,
        default=False,
        help_text="Solange dieser Haken nicht gesetzt ist, wird diese Meldung nicht angezeigt. "
        'Dieser Haken ist auch nötig, um eine Meldung mit dem Meldungstyp "Breaking" oder "Abend-Push"'
        " senden zu können.",
    )

    delivered_fb = models.CharField(
        "Breaking/Abend-Push: Facebook",
        null=False,
        blank=False,
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.NOT_SENT.value,
    )

    delivered_tg = models.CharField(
        "Breaking/Abend-Push: Telegram",
        null=False,
        blank=False,
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.NOT_SENT.value,
    )

    author = models.CharField("Autor", max_length=200, null=False)

    link = models.URLField(
        "Link",
        blank=True,
        null=True,
        max_length=500,
        default=None,
        help_text="Der Link wird am Ende einer Meldung (FB-Messenger und Letzte Meldung) "
        'mit dem Button-Text "MEHR 🌍" ausgespielt, '
        "respektive als Hyperlink hinter dem Schlagwort-Text nach dem Telegram-Text.",
    )

    audio = S3DirectField(
        "Audio-Feature",
        null=True,
        blank=True,
        dest="default",
        help_text="Dateiformat: *.mp3."
        " Das Audio zu dieser Meldung ist nach dem Intro-Text optional abrufbar.",
    )

    def is_quiz(self):
        return len(self.quiz_options.all()) > 1

    def __str__(self):
        emoji = "✅" if self.published else "🚫"

        if Report.Type(self.type) is Report.Type.BREAKING:
            emoji = "🚨"
        if Report.Type(self.type) is Report.Type.EVENING:
            emoji = "🌙"

        return f'{emoji} {self.created.strftime("%d.%m.%Y")} - ' f" {self.headline}"


class NotificationSent(models.Model):
    class Meta:
        verbose_name = "Empfänger"
        verbose_name_plural = "Empfänger"

    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        verbose_name="Meldung",
        related_name="notification_sent",
        related_query_name="notification_sent",
        primary_key=True,
    )

    fb = models.BooleanField("Facebook")
    tg = models.BooleanField("Telegram")

    morning = models.BooleanField("☕ Morgen")
    evening = models.BooleanField("🌙 Abend")
    breaking = models.BooleanField("🚨 Breaking")

    def __str__(self):
        timings = {"☕": self.morning, "🌙": self.evening, "🚨": self.breaking}
        timings = " ".join(emoji for emoji, status in timings.items() if status)

        return f"{timings}"


class ReportFragment(Fragment):
    class Meta:
        verbose_name = "Meldungs-Fragment"
        verbose_name_plural = "Meldungs-Fragmente"
        ordering = ("id",)

    report = models.ForeignKey(
        "Report",
        on_delete=models.CASCADE,
        related_name="fragments",
        related_query_name="fragment",
    )

    link_wiki = models.ForeignKey(
        "Wiki",
        models.SET_NULL,
        verbose_name="Einzelheit",
        related_name="+",
        related_query_name="+",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.report.headline} - {self.question}"


class ReportQuiz(Quiz):
    class Meta:
        verbose_name = "Quiz-Button"
        verbose_name_plural = "Quiz-Buttons"
        ordering = ("id",)

    report = models.ForeignKey(
        "Report",
        on_delete=models.CASCADE,
        related_name="quiz_options",
        related_query_name="quiz_options",
    )

    def __str__(self):
        return f"{self.report.headline} - {self.quiz_option}"
