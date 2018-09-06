from django.db import models

from .attachment import Attachment


class Quiz(Attachment):

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
        abstract = True

    correct_option = models.BooleanField('Richtige Antwort', blank=True, default=False)
    quiz_option = models.CharField('Quiz Option', max_length=20, null=True, blank=True)
    quiz_text = models.CharField('Quiz Antwort', max_length=640, null=False, blank=False)

