import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage


class S3BotoRandomNameStorage(S3Boto3Storage):
    def generate_filename(self, filename):
        filename = super().generate_filename(filename)
        extension = os.path.splitext(filename)[1]
        path = os.path.dirname(filename)
        return os.path.join(path, "%s%s") % (uuid.uuid4(), extension)
