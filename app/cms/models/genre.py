from django.db import models


class Genre(models.Model):
    """
    Meldungen werden einem Genre zugeordnet. Die Zuordnung ist verpflichtent.
    Die Zuordnung dient zur
    Ausspielung von Meldungen zu einem Genre und um ähnliche Nachrichten anzuzeigen.
    """

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    name = models.CharField("Name", max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name
