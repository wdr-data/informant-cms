from django.db import models


class ReportTag(models.Model):
    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return self.name
