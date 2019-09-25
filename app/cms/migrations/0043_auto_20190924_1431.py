# Generated by Django 2.2.5 on 2019-09-24 14:31

from django.db import migrations, models
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0042_auto_20190923_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='type',
            field=models.CharField(choices=[('regular', '📰 Reguläre Meldung'), ('breaking', '🚨 Breaking')], default='regular', help_text='Wird dieser Wert auf "Breaking" gesetzt UND ist die Meldung freigegeben, so wird die Meldung mit dem Sichern SOFORT als Breaking-Push gesendet!', max_length=20, verbose_name='Meldungstyp'),
        ),
        migrations.AlterField(
            model_name='report',
            name='audio',
            field=s3direct.fields.S3DirectField(blank=True, help_text='Dateiformat: *.mp3. Das Audio zu dieser Meldung ist nach dem Intro-Text optional abrufbar.', null=True, verbose_name='Audio-Feature'),
        ),
    ]