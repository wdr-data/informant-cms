# Generated by Django 2.0.6 on 2018-06-27 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0025_auto_20180625_1433"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="short_headline",
            field=models.CharField(
                default="", max_length=20, verbose_name="Button-Titel"
            ),
            preserve_default=False,
        ),
    ]
