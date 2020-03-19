from django.db import models

from .report import Report


class Subtype(models.Model):
    """
    Meldungen werden einem Genre zugeordnet. Die Zuordnung ist verpflichtent.
    Die Zuordnung dient zur
    Ausspielung von Meldungen zu einem Genre und um ähnliche Nachrichten anzuzeigen.
    """

    class Meta:
        verbose_name = 'Meldungs-Subtyp'
        verbose_name_plural = 'Meldungs-Subtypen'

    type = models.CharField(
        'Meldungstyp',
        null=False,
        blank=False,
        max_length=20,
        choices=[(Report.Type.REGULAR.value, '📰 Reguläre Meldung'),
                 (Report.Type.LAST.value, '🎨 Letzte Meldung'),
                 (Report.Type.BREAKING.value, '🚨 Breaking')],
        help_text='Hier kannst du wählen, zu welchem Meldungstyp dieser Subtyp gehört.',
        default=Report.Type.LAST.value)
    emoji = models.CharField('Emoji', max_length=3, null=False, blank=False)
    title = models.CharField('Titel', max_length=17, null=False, blank=False)

    def __str__(self):
        return f'{self.emoji} {self.title}'
