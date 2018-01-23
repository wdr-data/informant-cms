from django.db import models
from django.utils import timezone
from django.db import models
from datetime import datetime
from sortedm2m.fields import SortedManyToManyField


def default_pub_date():
    now = timezone.now()
    default = datetime(now.year, now.month, now.day, hour=18, minute=00)
    return default

class Push(models.Model):
    """
    Pushes fassen Meldungen zusammen. Diese Meldungen werden zum jeweils festgelegten Zeitpunkt
    an alle Abonnenten versandt.
    """

    class Meta:
        verbose_name = 'Push'
        verbose_name_plural = 'Pushes'

    pub_date = models.DateTimeField(
        'Push Zeitpunkt',
        default=default_pub_date)

    published = models.BooleanField(
        'Freigegeben', null=False, default=False,
        help_text='Solange dieser Haken nicht gesetzt ist, wird dieser Push nicht versendet, '
                  'auch wenn der konfigurierte Zeitpunkt erreicht wird.')

    breaking = models.BooleanField(
        'Breaking', null=False, default=False,
        help_text='Wird dieser Haken gesetzt UND ist der Push freigegeben,'
                  ' so wird der Push mit dem sichern SOFORT als Breaking-Push gesendet!')

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
