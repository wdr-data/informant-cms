# Generated by Django 2.2.9 on 2020-05-26 12:26

from django.db import migrations, models
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0064_auto_20200525_1236"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="original",
            field=s3direct.fields.S3DirectField(
                help_text="Zulässige Dateiformate: *.jpg, *.jpeg, *.png, *.mp3, *.mp4, *.gif",
                max_length=512,
                verbose_name="Medien-Anhang",
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="title",
            field=models.CharField(max_length=125, verbose_name="Titel"),
        ),
    ]
