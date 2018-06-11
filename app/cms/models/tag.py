from django.db import models
from ..references.dialogflow import add_entry, Entity


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        add_entry(self.name, Entity.TAGS, optional=True)
