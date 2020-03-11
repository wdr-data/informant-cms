from django.db import models

from .attachment import HasAttachment
from .genre import Genre
from .tag import ReportTag


class NewsBaseModel(HasAttachment):
    class Meta:
        abstract = True

    genres = models.ManyToManyField(Genre, related_name='%(class)s', verbose_name='Genre')
    tags = models.ManyToManyField(ReportTag, verbose_name='Tags', related_name='%(class)s', blank=True, help_text='Nach diesen Worten können Nutzer:innen im Bot fragen.')
    text = models.CharField('Intro-Text', max_length=2000, null=False)
