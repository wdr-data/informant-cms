from io import BytesIO
from os.path import dirname, abspath
from pathlib import Path

from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
from PIL import Image, ImageFont, ImageDraw

ASSETS_DIR = Path(dirname(dirname(abspath(__file__)))) / 'assets'

class Attachment(models.Model):
    """
    Zu einem Fragment kann ein Medien-Anhang
    """

    class Meta:
        abstract = True

    media_original = models.FileField('Medien-Anhang', null=True, blank=True)
    media_note = models.CharField('Credit', max_length=100, null=True, blank=True)

    media = models.FileField('Verarbeitet', null=True, blank=True)

    def update_attachment(self):
        if not self.media_original:
            self.media = None
            return

        if not self.media_note:
            self.media = self.media_original
            return

        response = requests.get(self.media_original.url)
        try:
            img = Image.open(BytesIO(response.content)).convert('RGBA')
        except:
            self.media = self.media_original
            raise

        draw = ImageDraw.Draw(img)

        fnt = ImageFont.truetype(ASSETS_DIR / 'Open_Sans' / 'OpenSans-Regular.ttf', 15)

        draw.text((10, 10), self.media_note, font=fnt, fill=(255, 255, 255, 255))

        bio = BytesIO()

        img.save(bio, 'JPEG')

        bio.seek(0)

        path = default_storage.save('', ContentFile(bio, name=self.media_original))
        self.media = path

