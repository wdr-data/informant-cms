# Generated by Django 2.2.5 on 2019-09-24 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0044_auto_20190924_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='delivered',
            field=models.BooleanField(default=True, help_text='Dieses Feld wird nur markiert, wenn eine Breaking Meldung erfolgreich versendet wurde.', verbose_name='Breaking Versendet'),
        ),
    ]