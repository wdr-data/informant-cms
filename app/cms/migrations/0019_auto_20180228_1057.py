# Generated by Django 2.0.2 on 2018-02-28 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0018_auto_20180202_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Verarbeitet'),
        ),
        migrations.AddField(
            model_name='push',
            name='media_note',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Credit'),
        ),
        migrations.AddField(
            model_name='push',
            name='media_original',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Medien-Anhang'),
        ),
    ]