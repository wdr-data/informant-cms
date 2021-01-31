import logging

from io import BytesIO
from os.path import dirname, abspath, splitext

from pathlib import Path
from urllib.parse import unquote

from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import requests
from requests.exceptions import MissingSchema
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from s3direct.fields import S3DirectField

ASSETS_DIR = Path(dirname(dirname(abspath(__file__)))) / "assets"


class Attachment(models.Model):
    class Meta:
        abstract = False
        verbose_name = "Medien-Anhang"
        verbose_name_plural = "Medien-Anhänge"

    title = models.CharField("Titel", max_length=125, null=False, blank=False)

    original = S3DirectField(
        "Medien-Anhang",
        null=False,
        blank=False,
        dest="default",
        help_text="Zulässige Dateiformate: *.jpg, *.jpeg, *.png, *.gif",
    )
    credit = models.CharField("Credit", max_length=100, null=True, blank=True)

    processed = models.FileField("Verarbeitet", max_length=512, null=True, blank=True)

    upload_date = models.DateTimeField("Hochgeladen am", auto_now_add=True)

    def __str__(self):
        extension = splitext(str(self.original))[-1]
        return f'{self.title}{extension}, {self.upload_date.strftime("%d.%m.%Y")}'

    @classmethod
    def process_attachment(cls, original, credit):
        if not original:
            return None, None

        filename = original
        original_url = default_storage.url(original)

        if not (
            filename.lower().endswith(".png")
            or filename.lower().endswith(".jpg")
            or filename.lower().endswith(".jpeg")
        ):
            return filename, original_url

        file_content = requests.get(original_url).content

        try:
            img = Image.open(BytesIO(file_content))
        except:
            logging.exception("Loading attachment for processing failed")
            return filename, original_url

        image_changed = False
        orig_mode = img.mode
        max_size = (1920, 1080)

        # Resize image
        if any(actual > max_ for actual, max_ in zip(img.size, max_size)):
            scale = min(max_ / actual for max_, actual in zip(max_size, img.size))

            new_size = tuple(int(dim * scale) for dim in img.size)
            img = img.resize(new_size, resample=Image.LANCZOS)
            image_changed = True

        # Draw credit onto image
        if credit:
            # Create initial image objects for text drawing
            img = img.convert("RGBA")
            alpha = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(alpha)

            # Configuration for text drawing
            the_text = "FOTO: " + str(credit).upper()
            fontsize = max((img.size[0] + img.size[1]) / 2 / 50, 10)
            shadow_radius = fontsize / 3
            shadow_mult = 0.75
            text_alpha = 0.7
            padding = tuple((int(shadow_radius * 2.5), int(shadow_radius * 3)))
            position = tuple(int(shadow_radius + p) for p in padding)

            fnt = ImageFont.truetype(
                str(ASSETS_DIR / "Open_Sans" / "OpenSans-SemiBold.ttf"), int(fontsize)
            )

            # Calculate size of text
            text_size = draw.textsize(the_text, font=fnt)

            # Create new, smaller image to draw the text on
            txt = Image.new(
                "RGBA",
                tuple(
                    ts + pad + pos for ts, pad, pos in zip(text_size, padding, position)
                ),
                (0, 0, 0, 0),
            )

            # Do the drawing
            draw = ImageDraw.Draw(txt)
            draw.text(position, the_text, font=fnt, fill=(0, 0, 0, 255))

            shadow = txt.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
            txt = shadow.point(lambda px: min(int(px * shadow_mult), 255))

            draw = ImageDraw.Draw(txt)
            draw.text(
                position,
                the_text,
                font=fnt,
                fill=(255, 255, 255, int(255 * text_alpha)),
            )

            # Rotate and paste onto original image
            txt = txt.rotate(90, expand=1, resample=Image.LANCZOS)
            alpha.paste(txt, box=tuple(a - b for a, b in zip(alpha.size, txt.size)))
            img = Image.alpha_composite(img, alpha)
            image_changed = True

        if not image_changed:
            return filename, original_url

        # Save result
        bio = BytesIO()
        bio.name = filename
        out = img.convert(orig_mode)
        out.save(bio)
        bio.seek(0)

        new_filename = default_storage.generate_filename(filename)
        path = default_storage.save(
            new_filename, ContentFile(bio.read(), name=new_filename)
        )
        url = default_storage.url(path)
        return path, url


class HasAttachment(models.Model):
    class Meta:
        abstract = True

    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.deletion.SET_NULL,
        related_name="+",
        related_query_name="+",
        null=True,
        blank=True,
        verbose_name="Medien-Anhang",
    )
