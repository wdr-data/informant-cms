# Generated by Django 2.2.9 on 2020-03-17 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0059_auto_20200312_1358"),
    ]

    operations = [
        migrations.AddField(
            model_name="push",
            name="link",
            field=models.URLField(
                blank=True,
                default=None,
                help_text='Der Link wird am Ende am Ende des Push-Outro angehangen. Der Button-Text lautet: "🔗 {Schlagwort-Link}".Dieser Link dient insbesondere der Cross-Promo von WDR-Inhalten.',
                max_length=500,
                null=True,
                verbose_name="DeepLink",
            ),
        ),
        migrations.AddField(
            model_name="push",
            name="link_name",
            field=models.CharField(
                blank=True, max_length=17, null=True, verbose_name="Schlagwort-Link"
            ),
        ),
    ]
