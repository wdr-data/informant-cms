# Generated by Django 3.1.5 on 2021-01-28 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0075_auto_20210127_0940"),
    ]

    operations = [
        migrations.AddField(
            model_name="faq",
            name="description",
            field=models.CharField(
                blank=True, max_length=400, verbose_name="Beschreibung"
            ),
        ),
    ]