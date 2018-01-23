from django.utils import timezone
from django.db import models

from .genre import Genre
from .topic import Topic


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)


class Report(models.Model):
    """
    Meldungen sind themenbezogene, in sich abgeschlossene Nachrichten.</p><p>
    Sie können aus mehreren Fragmenten bestehen. Um von einem Fragment zum nächsten zu gelangen,
    muss der Nutzer mit dem Bot interagieren, indem er einen Button mit einer weiterführenden Frage
    o.ä. anklickt.
    """

    class Meta:
        verbose_name = 'Meldung'
        verbose_name_plural = 'Meldungen'

    headline = models.CharField('Überschrift', max_length=200, null=False)
    genre = models.ManyToManyField(Genre, related_name='reports', verbose_name='Genre')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True,
                              related_name='reports', verbose_name='Thema')
    tags = models.ManyToManyField(ReportTag, related_name='items')
    text = models.CharField('Intro-Text', max_length=640, null=False)
    media = models.FileField('Medien-Anhang Intro', null=True, blank=True)
    media_note = models.CharField('Credit', max_length=100, null=True, blank=True)

    created = models.DateTimeField(
        'Erstellt',
        default=timezone.now)

    published = models.BooleanField(
        'Freigegeben', null=False, default=False,
        help_text='Solange dieser Haken nicht gesetzt ist, wird diese Meldung nicht versendet, '
                  'weder in terminierten Highlight-Pushes noch an Abonnenten von bestimmten '
                  'Sportarten, Sportlern, Disziplinen etc.')

    delivered = models.BooleanField(
        'Versendet', null=False, default=False)

    def __str__(self):
        return '%s - %s' % (self.created.strftime('%d.%m.%Y'), self.headline)

    @classmethod
    def last(cls, *, count=1, offset=0, only_published=True, delivered=False, by_date=True):
        reports = cls.objects.all()

        if only_published:
            reports = reports.filter(published=True)

        if not delivered:
            reports = reports.filter(delivered=False)

        if by_date:
            reports = reports.order_by('-created')
        else:
            reports = reports.order_by('-id')

        return reports[offset:count]


class ReportFragment(models.Model):

    class Meta:
        verbose_name = 'Meldungs-Fragment'
        verbose_name_plural = 'Meldungs-Fragmente'

    report = models.ForeignKey('Report', on_delete=models.CASCADE, related_name='fragments',
                               related_query_name='fragment')

    question = models.CharField('Frage', max_length=20, null=True, blank=True)
    text = models.CharField('Text', max_length=640, null=False, blank=False)
    media = models.FileField('Medien-Anhang', null=True, blank=True)
    media_note = models.CharField('Credit', max_length=100, null=True, blank=True)
  
    def __str__(self):
        return '%s - %s' % (self.report.headline, self.question)
