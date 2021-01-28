# Generated by Django 3.1.5 on 2021-01-26 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0071_auto_20210126_1018"),
    ]

    operations = [
        migrations.AddField(
            model_name="promo",
            name="short_headline",
            field=models.CharField(
                default="foobar",
                help_text="Titel des Buttons, der zu dieser Promo führt.",
                max_length=17,
                verbose_name="Button-Text",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="promo",
            name="link",
            field=models.URLField(
                blank=True,
                default=None,
                help_text="Der Link wird am Ende am Ende des Promo-Text als Button angehangen.",
                max_length=500,
                verbose_name="Link",
            ),
        ),
        migrations.AlterField(
            model_name="promo",
            name="link_name",
            field=models.CharField(
                blank=True,
                help_text="Optional. Wenn kein Link-Button-Text gesetzt ist, wird der Button-Text automatisch gesetzt.",
                max_length=17,
                verbose_name="Link-Button-Text",
            ),
        ),
    ]