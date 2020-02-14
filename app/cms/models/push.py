from enum import Enum

from django.db import models
from datetime import date
from sortedm2m.fields import SortedManyToManyField

from .attachment import Attachment


class Push(Attachment):
    """
    Pushes fassen Meldungen zusammen. Diese Meldungen werden zum jeweils festgelegten Zeitpunkt
    an alle Abonnenten versandt.
    """

    class Meta:
        verbose_name = 'Push'
        verbose_name_plural = 'Pushes'

    class Timing(Enum):
        MORNING = 'morning'
        EVENING = 'evening'
        BREAKING = 'breaking'
        TESTING = 'testing'

    class DeliveryStatus(Enum):
        NOT_SENT = 'not_sent'
        SENDING = 'sending'
        SENT = 'sent'

    pub_date = models.DateField(
        'Push Datum',
        default=date.today)

    timing = models.CharField(
        'Zeitpunkt', null=False, blank=False, max_length=20,
        choices=[(Timing.MORNING.value, '☕ Morgen'),
                 (Timing.EVENING.value, '🌙 Abend'),
                 (Timing.BREAKING.value, '🚨 Breaking'),
                 (Timing.TESTING.value, '⚗️ Test')],
        default=Timing.MORNING.value)

    published = models.BooleanField(
        'Freigegeben', null=False, default=False,
        help_text='Solange dieser Haken nicht gesetzt ist, wird dieser Push nicht versendet, '
                  'auch wenn der konfigurierte Zeitpunkt erreicht wird.')

    headline = models.CharField('Arbeitstitel', max_length=200, null=False,
                                help_text='Dieser Titel wird nicht ausgespielt')

    intro = models.CharField('Intro-Text', max_length=1000, null=False, blank=True)
    outro = models.CharField('Outro-Text', max_length=2000, null=False, blank=True)

    reports = SortedManyToManyField(
        'Report', related_name='pushes', verbose_name='Meldungen',
        help_text='Bitte maximal 4 Meldungen auswählen.')

    last_report = models.ForeignKey('Report', models.SET_NULL, verbose_name='Zum Schluss',
        related_name='+', related_query_name='+', null=True, blank=True)

    delivered_fb = models.CharField(
        'Facebook', null=False, blank=False, max_length=20,
        choices=[(DeliveryStatus.NOT_SENT.value, 'nicht gesendet'),
                 (DeliveryStatus.SENDING.value, 'wird gesendet'),
                 (DeliveryStatus.SENT.value, 'gesendet')],
        default=DeliveryStatus.NOT_SENT.value)

    delivered_date_fb = models.DateTimeField('Versand-Datum Facebook', null=True)

    delivered_tg = models.CharField(
        'Telegram', null=False, blank=False, max_length=20,
        choices=[(DeliveryStatus.NOT_SENT.value, 'nicht gesendet'),
                 (DeliveryStatus.SENDING.value, 'wird gesendet'),
                 (DeliveryStatus.SENT.value, 'gesendet')],
        default=DeliveryStatus.NOT_SENT.value)

    delivered_date_tg = models.DateTimeField('Versand-Datum Telegram', null=True)

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)

    @classmethod
    def last(cls, *, count=1, offset=0, only_published=True, delivered=False, by_date=True, breaking=True):
        pushes = cls.objects.all()

        if only_published:
            pushes = pushes.filter(published=True)

        if not breaking:
            pushes = pushes.exclude(timing='breaking')

        if not delivered:
            pushes = pushes.filter(
                delivered_fb=Push.DeliveryStatus.NOT_SENT.value,
                delivered_tg=Push.DeliveryStatus.NOT_SENT.value)

        if by_date:
            pushes = pushes.order_by('-pub_date', 'timing')
        else:
            pushes = pushes.order_by('-id')

        return pushes[offset:count]
