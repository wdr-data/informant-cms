from django.db import models

from .attachment import Attachment
from .genre import Genre
from .tag import ReportTag


class NewsBaseModel(Attachment):
    class Meta:
        abstract = True

    genres = models.ManyToManyField(Genre, related_name='%(class)s', verbose_name='Genre')
    tags = models.ManyToManyField(ReportTag, verbose_name='Tags', related_name='%(class)s', blank=True)
    text = models.CharField('Intro-Text', max_length=2000, null=False)
