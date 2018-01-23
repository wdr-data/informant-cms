from django.db import models


class Attachement(models.Model):
    """
    Zu einem Fragment kann ein Medien-Anhang
    """

    class Meta:
        abstract = True

    media = models.FileField('Medien-Anhang', null=True, blank=True)
    media_note = models.CharField('Credit', max_length=100, null=True, blank=True)
