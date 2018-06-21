from django.db import models
from ..references.dialogflow import add_entry, delete_entry, Entity


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if it's a new object
        if self.pk is not None:
            delete_entry(self.name, Entity.TAGS, optional=True)

        super().save(*args, **kwargs)

        add_entry(self.name, Entity.TAGS, optional=True)
