# Generated by Django 2.1.1 on 2018-09-07 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0037_auto_20180906_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportquiz',
            name='correct_option',
            field=models.BooleanField(blank=True, default=False, verbose_name='Richtige Antwort'),
        ),
    ]