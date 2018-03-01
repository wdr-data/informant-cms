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

    pub_date = models.DateField(
        'Push Datum',
        default=date.today)

    timing = models.CharField(
        'Zeitpunkt', null=False, blank=False, max_length=20,
        choices=[(Timing.MORNING.value, '🌇 Morgen'),
                 (Timing.EVENING.value, '🌆 Abend'),
                 (Timing.BREAKING.value, '🚨 Breaking')],
        help_text='Wird dieser Wert auf "Breaking" gesetzt UND ist der Push freigegeben,'
                  ' so wird der Push mit dem Sichern SOFORT als Breaking-Push gesendet!',
        default=Timing.MORNING.value)

    published = models.BooleanField(
        'Freigegeben', null=False, default=False,
        help_text='Solange dieser Haken nicht gesetzt ist, wird dieser Push nicht versendet, '
                  'auch wenn der konfigurierte Zeitpunkt erreicht wird.')

    headline = models.CharField('Arbeitstitel', max_length=200, null=False,
                                help_text='Dieser Titel wird nicht ausgespielt')

    intro = models.CharField('Intro-Text', max_length=640, null=False, blank=True)
    outro = models.CharField('Outro-Text', max_length=640, null=False, blank=True)

    reports = SortedManyToManyField('Report', related_name='pushes', verbose_name='Meldungen')

    delivered = models.BooleanField('Versendet', null=False, default=False)

    def __str__(self):
        return '%s - %s' % (self.pub_date.strftime('%d.%m.%Y'), self.headline)

    @classmethod
    def last(cls, *, count=1, offset=0, only_published=True, delivered=False, by_date=True):
        pushes = cls.objects.all()

        if only_published:
            pushes = pushes.filter(published=True)

        if not delivered:
            pushes = pushes.filter(delivered=False)

        if by_date:
            pushes = pushes.order_by('-pub_date')
        else:
            pushes = pushes.order_by('-id')

        return pushes[offset:count]
