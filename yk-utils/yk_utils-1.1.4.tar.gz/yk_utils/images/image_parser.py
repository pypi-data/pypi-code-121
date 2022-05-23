"""Image parser module.
"""
import os
import base64


def parse_image(image) -> str:
    """Check whether the image is a string or a file path or a file-like object.
    :param image:
        A base64 string or a file path or a file-like object representing an image.
    :return:
        Image as a base64 string.
    """
    data = None
    if hasattr(image, 'read'):  # When image is a file-like object.
        data = image.read()
    elif os.path.isfile(image):  # When image is a file path.
        with open(image, 'rb') as file:
            data = file.read()

    return base64.b64encode(data).decode('utf-8') if data else image
