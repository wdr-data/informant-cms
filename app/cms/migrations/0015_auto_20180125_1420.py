# Generated by Django 2.0.1 on 2018-01-25 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0014_auto_20180125_1422"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportfragment",
            name="link_wiki",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                related_query_name="+",
                to="cms.Wiki",
                verbose_name="Einzelheit",
            ),
        ),
    ]
