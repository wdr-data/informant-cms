# Generated by Django 2.0.8 on 2018-09-06 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0036_merge_20180905_1639"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reportquiz",
            name="quiz_option",
            field=models.CharField(
                default="N/A", max_length=20, verbose_name="Quiz Option"
            ),
            preserve_default=False,
        ),
    ]
