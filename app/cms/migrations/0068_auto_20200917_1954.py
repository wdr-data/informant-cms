# Generated by Django 2.2.9 on 2020-09-17 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0067_auto_20200917_1931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='push',
            options={'verbose_name': 'Push', 'verbose_name_plural': 'Morgen-Pushes'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-created'], 'verbose_name': 'Meldung', 'verbose_name_plural': 'Meldungen, Eilmeldungen und Abend-Content-Push'},
        ),
    ]