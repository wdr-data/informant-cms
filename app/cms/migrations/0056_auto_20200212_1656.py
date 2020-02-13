# Generated by Django 2.2.10 on 2020-02-12 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0055_auto_20200212_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='delivered_date_tg',
            field=models.DateTimeField(null=True, verbose_name='Versand-Datum Telegram'),
        ),
        migrations.AddField(
            model_name='push',
            name='delivered_tg',
            field=models.CharField(choices=[('not_sent', 'nicht gesendet'), ('sending', 'wird gesendet'), ('sent', 'gesendet')], default='not_sent', max_length=20, verbose_name='Telegram'),
        ),
        migrations.AddField(
            model_name='report',
            name='delivered_tg',
            field=models.CharField(choices=[('not_sent', 'nicht gesendet'), ('sending', 'wird gesendet'), ('sent', 'gesendet')], default='not_sent', max_length=20, verbose_name='Breaking: Telegram'),
        ),
    ]