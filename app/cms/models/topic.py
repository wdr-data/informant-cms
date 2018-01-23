from django.db import models


class Topic(models.Model):
    """
    Meldungen werden einem eindeutigen Thema zugeordnet.
    Die Zuordnung dient zur
    Ausspielung von Meldungen zu einem Thema und um ähnliche Nachrichten anzuzeigen.
    """

    class Meta:
        verbose_name = 'Thema'
        verbose_name_plural = 'Themen'

    name = models.CharField('Name', max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name
