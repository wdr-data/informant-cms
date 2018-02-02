from datetime import timedelta

from django.db import models
from django.utils import timezone

from .attachment import Attachment
from .genre import Genre
from .topic import Topic
from .report import ReportTag
from .fragment import Fragment


def default_follow_up_at():
    return timezone.now() + timedelta(weeks=4)


class Wiki(Attachment):
    """
    Wikis sind Nachschlagewerke für weiterführende Erklärungen.
    """

    class Meta:
        verbose_name = 'Wiki'
        verbose_name_plural = 'Wikis'

    name = models.CharField('Titel', max_length=200, null=False)

    follow_up_at = models.DateTimeField('Wiedervorlage',
                                        default=default_follow_up_at)

    genres = models.ManyToManyField(Genre, related_name='wikis', verbose_name='Genre')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='wikis', verbose_name='Thema')
    tags = models.ManyToManyField(ReportTag, verbose_name='Tags', related_name='wikis', blank=True)
    text = models.CharField('Intro-Text', max_length=640, null=False)

    def __str__(self):
        return f'{self.name}'


class WikiFragment(Fragment):

    class Meta:
        verbose_name = 'Wiki-Fragment'
        verbose_name_plural = 'Wiki-Fragmente'
        ordering = ('id', )

    wiki = models.ForeignKey('Wiki', on_delete=models.CASCADE, related_name='fragments',
                             related_query_name='fragment')
    link_wiki = models.ForeignKey('Wiki', models.SET_NULL, verbose_name='Link Einzelheit',
                                  related_name='+', related_query_name='+', null=True, blank=True)

    def __str__(self):
        return f'{self.wiki.name} - {self.question}'
