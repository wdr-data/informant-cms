# Generated by Django 2.0.1 on 2018-01-23 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0007_auto_20180123_1715"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="media",
            field=models.FileField(
                blank=True, null=True, upload_to="", verbose_name="Medien-Anhang"
            ),
        ),
    ]
