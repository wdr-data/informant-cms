# Generated by Django 2.0.1 on 2018-01-25 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0010_auto_20180124_1209"),
    ]

    operations = [
        migrations.CreateModel(
            name="FAQ",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "media_original",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="",
                        verbose_name="Medien-Anhang",
                    ),
                ),
                (
                    "media_note",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Credit"
                    ),
                ),
                (
                    "media",
                    models.FileField(
                        blank=True, null=True, upload_to="", verbose_name="Verarbeitet"
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Begriff")),
                (
                    "slug",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="Slug"
                    ),
                ),
                ("text", models.CharField(max_length=640, verbose_name="Intro-Text")),
            ],
            options={
                "verbose_name": "FAQ",
                "verbose_name_plural": "FAQs",
            },
        ),
        migrations.CreateModel(
            name="FAQFragment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "media_original",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="",
                        verbose_name="Medien-Anhang",
                    ),
                ),
                (
                    "media_note",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Credit"
                    ),
                ),
                (
                    "media",
                    models.FileField(
                        blank=True, null=True, upload_to="", verbose_name="Verarbeitet"
                    ),
                ),
                (
                    "question",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="Frage"
                    ),
                ),
                ("text", models.CharField(max_length=640, verbose_name="Text")),
                (
                    "faq",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fragments",
                        related_query_name="fragment",
                        to="cms.FAQ",
                    ),
                ),
                (
                    "link_faq",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        related_query_name="+",
                        to="cms.FAQ",
                    ),
                ),
            ],
            options={
                "verbose_name": "FAQ-Fragment",
                "verbose_name_plural": "FAQ-Fragmente",
            },
        ),
    ]
