import logging

from django.db import models
from ..references.dialogflow import add_entity, delete_entity, EntityType


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
            formerTag = self.__class__.objects.get(pk=self.pk)
            try:
                delete_entity(formerTag.name, EntityType.TAGS)
            except Exception as e:
                logging.error(e)

        super().save(*args, **kwargs)

        try:
            add_entity(self.name, EntityType.TAGS)
        except Exception as e:
            logging.error(e)
