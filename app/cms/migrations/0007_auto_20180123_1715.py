# Generated by Django 2.0.1 on 2018-01-23 17:15

import cms.models.push
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_auto_20180123_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push',
            name='breaking',
            field=models.BooleanField(default=False, help_text='Wird dieser Haken gesetzt UND ist der Push freigegeben, so wird der Push mit dem sichern SOFORT als Breaking-Push gesendet!', verbose_name='Breaking'),
        ),
        migrations.AlterField(
            model_name='push',
            name='headline',
            field=models.CharField(help_text='Dieser Titel wird nicht ausgespielt', max_length=200, verbose_name='Arbeitstitel'),
        ),
        migrations.AlterField(
            model_name='push',
            name='pub_date',
            field=models.DateTimeField(default=cms.models.push.default_pub_date, verbose_name='Push Zeitpunkt'),
        ),
    ]