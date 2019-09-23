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
        verbose_name_plural = 'Meldungen'
        ordering = ['-created']

    headline = models.CharField('Überschrift', max_length=200, null=False)
    short_headline = models.CharField(
        'Button-Text', max_length=17, null=False,
        help_text='Dies ist der Text, der auf dem Auswahl-Button für diese Nachricht angezeigt '
                  'wird. Bitte möglichst kurzes Schlagwort eintragen.')

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
        help_text='Solange dieser Haken nicht gesetzt ist, wird diese Meldung nicht versendet, '
                  'weder in terminierten Highlight-Pushes noch an Abonnenten von bestimmten '
                  'Sportarten, Sportlern, Disziplinen etc.')

    delivered = models.BooleanField(
        'Versendet', null=False, default=True)

    author = models.CharField('Autor', max_length=200, null=False)

    link = models.URLField('DeepLink', blank=True, null=True, max_length=500, default=None,
                           help_text= 'Der Link wird am Ende einer Meldung angehangen.'
                                      ' Der Button-Text lautet "MEHR 🌍".'
                           )

    audio = S3DirectField('Audio-Feature', null=True, blank=True, dest='default',
                          help_text='Das Audio-Feature zu dieser Meldung ist nach dem Intro-Text optional abrufbar.')

    def is_quiz(self):
        return len(self.quiz_options.all()) > 1

    def __str__(self):
        return f'{"✅" if self.published else "🚫"} {self.created.strftime("%d.%m.%Y")} - ' \
               f' {self.headline}'

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
