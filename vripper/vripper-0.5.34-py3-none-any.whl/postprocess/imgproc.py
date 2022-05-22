import logging
import os

from PIL import Image, UnidentifiedImageError
from commmons import with_prefix, get_filesize_in_bytes
from resizeimage import resizeimage

from vripper.enum.processingpriority import ProcessingPriority
from vripper.model.vparams import VParams

logger = logging.getLogger("vripper")


def _get_new_size(size, max_dimension: int):
    w, h = size
    if w > h:
        height = h * max_dimension / w
        width = max_dimension
    else:
        width = w * max_dimension / h
        height = max_dimension

    # Do not upscale
    if w <= width or h <= height:
        return None

    return int(width), int(height)


def has_enough_pixels(path, min_dimension=0):
    # Is there a cheaper way to do this check?
    try:
        with open(path, 'r+b') as f:
            with Image.open(f) as image:
                return min(image.size) > min_dimension
    except (UnidentifiedImageError, FileNotFoundError):
        pass
    return False


def process_then_return_new_path(path: str, vparams: VParams):
    tmp_path = path + ".tmp.jpg"
    if os.path.exists(tmp_path):
        # Windows FS API does not allow overwrites
        os.remove(tmp_path)
    with open(path, 'r+b') as f:
        with Image.open(f) as image:
            if vparams.max_dimension:
                new_size = _get_new_size(image.size, vparams.max_dimension)
                if new_size:
                    image = resizeimage.resize_contain(image, new_size)
            image.convert("RGB").save(tmp_path, quality=vparams.quality)
    return tmp_path


def is_valid_image(path):
    return has_enough_pixels(path, 0)


def process_with_constraints(path, vparams):
    image_logger = with_prefix(logger, path.split("/")[-1])

    if not is_valid_image(path):
        image_logger.error("Cannot read the image. This is possibly a corrupted file.")
        return

    filesize = get_filesize_in_bytes(path)
    if vparams.acceptable_filesize is not None and filesize <= vparams.acceptable_filesize:
        image_logger.debug(f"The file is already small enough. filesize={filesize}")
        return

    new_path = process_then_return_new_path(path, vparams)

    should_replace = True
    if vparams.priority == ProcessingPriority.SMALLER_FILESIZE:
        old_size = get_filesize_in_bytes(path)
        new_size = get_filesize_in_bytes(new_path)
        should_replace = new_size < old_size

        image_logger.debug(f"should_replace={should_replace} old_size={old_size} new_size={new_size}")

    if should_replace:
        os.replace(new_path, path)
    else:
        os.remove(new_path)
