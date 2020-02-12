from enum import Enum

from django.utils import timezone
from django.db import models
from s3direct.fields import S3DirectField

from .news_base import NewsBaseModel
from .fragment import Fragment
from .quiz import Quiz


class Report(NewsBaseModel):
    """
    Meldungen sind themenbezogene, in sich abgeschlossene Nachrichten.</p><p>
    Sie können aus mehreren Fragmenten bestehen. Um von einem Fragment zum nächsten zu gelangen,
    muss der Nutzer mit dem Bot interagieren, indem er einen Button mit einer weiterführenden Frage
    o.ä. anklickt.
    """

    class Meta:
        verbose_name = 'Meldung'
        verbose_name_plural = 'Meldungen und Eilmeldungen'
        ordering = ['-created']

    class Type(Enum):
        REGULAR = 'regular'
        BREAKING = 'breaking'

    class DeliveryStatus(Enum):
        NOT_SENT = 'not_sent'
        SENDING = 'sending'
        SENT = 'sent'

    type = models.CharField(
        'Meldungstyp', null=False, blank=False, max_length=20,
        choices=[(Type.REGULAR.value, '📰 Reguläre Meldung'),
                 (Type.BREAKING.value, '🚨 Breaking')],
        help_text='Wird dieser Wert auf "Breaking" gesetzt und die Meldung freigegeben, '
                  'kann sie als Breaking versendet werden.',
        default=Type.REGULAR.value)

    headline = models.CharField('Überschrift', max_length=200, null=False)

    summary = models.CharField(
        'Telegram-Text', max_length=900, null=False,
        help_text='Dieser Text wird bei Telegram als Meldungstext zusammen mit der Überschrift ausgespielt.')

    short_headline = models.CharField(
        'Schlagwort-Button', max_length=17, null=False,
        help_text='Hinter diesem Schlagwort wird in TG der Deeplink gesetzt. Außerdem ist dies der Text,'
                  ' der auf dem Auswahl-Button für diese Nachricht angezeigt in FB angezeigt wird.')

    created = models.DateTimeField(
        'Erstellt',
        default=timezone.now)
    published_date = models.DateTimeField(
        'Veröffentlicht', null=True,
    )
    modified = models.DateTimeField(
        'Bearbeitet', null=False,
    )

    published = models.BooleanField(
        'Freigegeben', null=False, default=False,
        help_text='Solange dieser Haken nicht gesetzt ist, wird diese Meldung nicht angezeigt. '
                  'Dieser Haken ist auch nötig, um eine Meldung mit dem Meldungstyp "Breaking"'
                  ' an alle Breaking-Abonnenten senden zu können.')

    delivered_fb = models.CharField(
        'Breaking: Facebook', null=False, blank=False, max_length=20,
        choices=[(DeliveryStatus.NOT_SENT.value, 'nicht gesendet'),
                 (DeliveryStatus.SENDING.value, 'wird gesendet'),
                 (DeliveryStatus.SENT.value, 'gesendet')],
        default=DeliveryStatus.NOT_SENT.value)

    author = models.CharField('Autor', max_length=200, null=False)

    link = models.URLField('DeepLink', blank=True, null=True, max_length=500, default=None,
                           help_text= 'Der Link wird am Ende einer Meldung angehangen und '
                                      'liefert dem Nutzer mehr Infos zur Meldung.'
                                      ' Der Button-Text lautet "MEHR 🌍".'
                           )

    audio = S3DirectField('Audio-Feature', null=True, blank=True, dest='default',
                          help_text='Dateiformat: *.mp3.'
                                    ' Das Audio zu dieser Meldung ist nach dem Intro-Text optional abrufbar.')

    def is_quiz(self):
        return len(self.quiz_options.all()) > 1

    def __str__(self):
        emoji = '✅' if self.published else '🚫'

        if Report.Type(self.type) is Report.Type.BREAKING:
            emoji = '🚨'

        return f'{emoji} {self.created.strftime("%d.%m.%Y")} - ' \
               f' {self.headline}'

class ReportFragment(Fragment):

    class Meta:
        verbose_name = 'Meldungs-Fragment'
        verbose_name_plural = 'Meldungs-Fragmente'
        ordering = ('id', )

    report = models.ForeignKey('Report', on_delete=models.CASCADE, related_name='fragments',
                               related_query_name='fragment')

    link_wiki = models.ForeignKey('Wiki', models.SET_NULL, verbose_name='Einzelheit',
                                  related_name='+', related_query_name='+', null=True, blank=True)

    def __str__(self):
        return f'{self.report.headline} - {self.question}'


class ReportQuiz(Quiz):

    class Meta:
        verbose_name = 'Quiz-Button'
        verbose_name_plural = 'Quiz-Buttons'
        ordering = ('id', )

    report = models.ForeignKey('Report', on_delete=models.CASCADE, related_name='quiz_options',
                               related_query_name='quiz_options')

    def __str__(self):
        return f'{self.report.headline} - {self.quiz_option}'
