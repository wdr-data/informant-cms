from datetime import timedelta

from django.db import models
from django.utils import timezone

from .newsbase import NewsBaseModel
from .fragment import Fragment


def default_follow_up_at():
    return timezone.now() + timedelta(weeks=4)


class Wiki(NewsBaseModel):
    """
    Wikis sind Nachschlagewerke für weiterführende Erklärungen.
    """

    class Meta:
        verbose_name = 'Wiki'
        verbose_name_plural = 'Wikis'

    name = models.CharField('Titel', max_length=200, null=False)

    follow_up_at = models.DateTimeField('Wiedervorlage',
                                        default=default_follow_up_at)

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
