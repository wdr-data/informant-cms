# Generated by Django 2.0.7 on 2018-07-19 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0028_auto_20180717_1413"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="topic",
        ),
        migrations.RemoveField(
            model_name="wiki",
            name="topic",
        ),
        migrations.AlterField(
            model_name="report",
            name="short_headline",
            field=models.CharField(
                help_text="Dies ist der Text, der auf dem Auswahl-Button für diese Nachricht angezeigt wird. Bitte möglichst kurzes Schlagwort eintragen.",
                max_length=17,
                verbose_name="Button-Text",
            ),
        ),
        migrations.DeleteModel(
            name="Topic",
        ),
    ]
