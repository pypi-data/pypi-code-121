import base64
import re
import six
import uuid
from tempfile import NamedTemporaryFile
from PIL import Image

from django.core.files.base import ContentFile
from django.db.models import ImageField
from rest_framework import serializers

WITH = 768
HEIGHT = 573


class SplintImageField(ImageField):
    """SplintImageField.

        Provide image width, height (at least one dim) and quality to resize
        image using PIL.

        Vertical crop will be applied before resizing the image.

        Usage: thumbnail = SplintImageField(
            'Thumbnail', upload_to='track', null=True, blank=True, width=120)
    """

    def __init__(self, *args, quality=80, width=WITH, vertical_crop=None,
                 height=None, **kwargs):
        """Override init to add quality and width, height information"""
        self.quality = quality
        self.width = width
        self.height = height
        self.vertical_crop = vertical_crop

        super().__init__(*args, ** kwargs)

    def pre_save(self, model_instance, add):
        """Optmize image saved.

        If you pass both width and height, aspect ration will be lost. You
        should provide at least one dimension (width or height).
        """
        # file = super().pre_save(model_instance, add)
        file = getattr(model_instance, self.attname)

        if file and bool(file.name):
            try:
                opened_image = file.file
                opened_image.open()
            except (OSError, IOError):
                return file

            im = Image.open(opened_image)

            if not file._committed or self.width != im.width:
                if im.format == 'PNG':
                    CONVERT = 'P'
                    FORMAT = 'PNG'
                    EXTENSION = 'png'
                else:
                    CONVERT = 'RGB'
                    FORMAT = 'JPEG'
                    EXTENSION = 'jpe'
                assert self.width or self.height
                width, height = self.width, self.height

                im = self.crop_image(im)

                if width is None:
                    width = int(im.width * height / im.height)
                if height is None:
                    height = int(im.height * width / im.width)

                width = min(width, im.width)
                height = min(height, im.height)
                im = im.resize((width, height), Image.ANTIALIAS)

                with NamedTemporaryFile() as temp_file:
                    # Force image convertion to JPEG
                    im = im.convert(CONVERT)
                    im.save(temp_file, quality=self.quality, format=FORMAT)
                    file.save(
                        f'{re.split("[_.]+", file.name)[0].rsplit("/", 1)[-1]}.{EXTENSION}',
                        temp_file, save=False)

        return file

    def crop_image(self, im):
        """Crop will be applied before resizing the image."""
        if self.vertical_crop and self.vertical_crop * 2 < im.height:
            im = im.crop((
                0, self.vertical_crop,
                im.width - 1, im.height - self.vertical_crop - 1
            ))
        return im


class SplintBase64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        """File conversion from base64."""
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(SplintBase64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        """Return file extension."""
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension
