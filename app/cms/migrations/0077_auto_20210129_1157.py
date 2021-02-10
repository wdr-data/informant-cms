# Generated by Django 3.1.5 on 2021-01-29 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0076_faq_description"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="report",
            options={
                "ordering": ["-created"],
                "verbose_name": "Meldung",
                "verbose_name_plural": "Push-Meldungen und Benachrichtigungen",
            },
        ),
        migrations.AlterField(
            model_name="report",
            name="type",
            field=models.CharField(
                choices=[
                    ("regular", "📰 Reguläre Meldung"),
                    ("last", "🎨 Letzte Meldung"),
                    ("breaking", "🚨 Breaking"),
                    ("evening", "🌙 Abend-Push"),
                    ("notification", "📨 Benachrichtigung"),
                ],
                default="evening",
                help_text='Wird dieser Wert auf "Breaking", "Abend-Push" oder "Benachrichtigung" gesetzt und die Meldung freigegeben, kann sie direkt versendet werden.',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="teaser",
            name="headline",
            field=models.CharField(
                help_text="Bei Telegram wird die erste Zeile gefettet. Bei Facebook ist die erste Zeile abgesetzt. In beiden Fällen wird automatisch ein ➡️ vorangestellt.",
                max_length=100,
                verbose_name="Leadsatz",
            ),
        ),
        migrations.AlterField(
            model_name="teaser",
            name="text",
            field=models.CharField(
                blank=True,
                help_text="Der Leadsatz in Kombination mit dem Text sollen als Fließtext zu lesen sein.",
                max_length=400,
                verbose_name="Text",
            ),
        ),
    ]