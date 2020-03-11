from django.db import models

from .attachment import HasAttachment


class Fragment(HasAttachment):

    class Meta:
        verbose_name = 'Fragment'
        verbose_name_plural = 'Fragmente'
        abstract = True

    question = models.CharField('Frage', max_length=20, null=True, blank=True)
    text = models.CharField('Text', max_length=2000, null=False, blank=False)
