# Generated by Django 2.0.3 on 2018-09-05 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0033_auto_20180904_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportquiz',
            name='correct_option',
            field=models.BooleanField(default=False, verbose_name='Richtige Antwort'),
        ),
    ]