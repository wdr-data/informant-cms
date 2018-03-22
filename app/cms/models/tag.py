from django.db import models
from ..references.dialogflow import get_entity_uuid, add_entry, Entity


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        genre_uuid = get_entity_uuid(Entity.TAGS)
        add_entry(self.name, genre_uuid)
