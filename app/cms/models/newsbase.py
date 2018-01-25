from django.db import models

from .attachment import Attachment
from .genre import Genre
from .topic import Topic
from .tag import ReportTag


class NewsBaseModel(Attachment):
    class Meta:
        abstract = True

    genres = models.ManyToManyField(Genre, related_name='%(class)s', verbose_name='Genre')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='%(class)s', verbose_name='Thema')
    tags = models.ManyToManyField(ReportTag, verbose_name='Tags', related_name='%(class)s', blank=True)
    text = models.CharField('Intro-Text', max_length=640, null=False)
