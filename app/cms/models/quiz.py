from django.db import models

from .attachment import HasAttachment


class Quiz(HasAttachment):

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
        abstract = True

    correct_option = models.BooleanField('Richtige Antwort', blank=True, default=False)
    quiz_option = models.CharField('Quiz Option', max_length=20, null=False, blank=False)
    quiz_text = models.CharField('Quiz Antwort', max_length=2000, null=False, blank=False)

