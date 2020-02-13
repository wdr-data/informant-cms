# Generated by Django 2.2.10 on 2020-02-13 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0056_auto_20200212_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='last_report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', related_query_name='+', to='cms.Report', verbose_name='Zum Schluss'),
        ),
        migrations.AlterField(
            model_name='report',
            name='type',
            field=models.CharField(choices=[('regular', '📰 Reguläre Meldung'), ('last', '🙈 Zum Schluss'), ('breaking', '🚨 Breaking')], default='regular', help_text='Wird dieser Wert auf "Breaking" gesetzt und die Meldung freigegeben, kann sie als Breaking versendet werden.', max_length=20, verbose_name='Meldungstyp'),
        ),
    ]
