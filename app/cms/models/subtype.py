from django.db import models


class Subtype(models.Model):
    """
    Meldungen werden einem Genre zugeordnet. Die Zuordnung ist verpflichtent.
    Die Zuordnung dient zur
    Ausspielung von Meldungen zu einem Genre und um ähnliche Nachrichten anzuzeigen.
    """

    class Meta:
        verbose_name = 'Meldungs-Subtyp'
        verbose_name_plural = 'Meldungs-Subtypen'

    emoji = models.CharField('Emoji', max_length=3, null=False, blank=False)
    title = models.CharField('Titel', max_length=17, null=False, blank=False)

    def __str__(self):
        return f'{self.emoji} {self.title}'
