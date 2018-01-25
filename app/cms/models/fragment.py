from django.db import models

from .attachment import Attachment


class Fragment(Attachment):

    class Meta:
        verbose_name = 'Fragment'
        verbose_name_plural = 'Fragmente'
        abstract = True

    question = models.CharField('Frage', max_length=20, null=True, blank=True)
    text = models.CharField('Text', max_length=640, null=False, blank=False)
