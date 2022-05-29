"""Image utils."""
import logging

from PIL import Image

log = logging.getLogger('imagex')
logging.basicConfig(level=logging.INFO)


def crop(
    original_image_file,
    cropped_image_file,
    left_top,
    width_height,
):
    """Crop."""
    left, top = left_top
    width, height = width_height
    _im = Image.open(original_image_file)
    cropped_im = _im.crop((left, top, left + width, top + height))
    cropped_im.save(cropped_image_file)
    log.info('Saved cropped image to %s', cropped_image_file)


def resize(
    original_image_file,
    resized_image_file,
    width_height,
):
    """Resize."""
    _im = Image.open(original_image_file)
    resized_im = _im.resize(width_height)
    resized_im.save(resized_image_file)
    log.info('Saved resized image to %s', resized_image_file)
