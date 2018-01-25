from django.utils import timezone
from django.db import models

from .genre import Genre
from .topic import Topic
from .attachment import Attachment
from .fragment import Fragment


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return self.name

class Report(Attachment):
    """
    Meldungen sind themenbezogene, in sich abgeschlossene Nachrichten.</p><p>
    Sie können aus mehreren Fragmenten bestehen. Um von einem Fragment zum nächsten zu gelangen,
    muss der Nutzer mit dem Bot interagieren, indem er einen Button mit einer weiterführenden Frage
    o.ä. anklickt.
    """

    class Meta:
        verbose_name = 'Meldung'
        verbose_name_plural = 'Meldungen'
        ordering = ['-created']

    headline = models.CharField('Überschrift', max_length=200, null=False)
    genres = models.ManyToManyField(Genre, related_name='reports', verbose_name='Genre')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='reports', verbose_name='Thema')
    tags = models.ManyToManyField(ReportTag, verbose_name='Tags', related_name='items')
    text = models.CharField('Intro-Text', max_length=640, null=False)

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


class ReportFragment(Fragment):

    class Meta:
        verbose_name = 'Meldungs-Fragment'
        verbose_name_plural = 'Meldungs-Fragmente'

    report = models.ForeignKey('Report', on_delete=models.CASCADE, related_name='fragments',
                               related_query_name='fragment')

    link_wiki = models.ForeignKey('Wiki', models.SET_NULL, verbose_name='Einzelheit',
                                  related_name='+', related_query_name='+', null=True, blank=True)

    def __str__(self):
        return f'{self.report.headline} - {self.question}'
