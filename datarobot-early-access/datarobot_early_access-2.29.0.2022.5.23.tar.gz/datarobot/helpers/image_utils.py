#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import io

import numpy as np

from datarobot.enums import (
    DEFAULT_VISUAL_AI_FORCE_SIZE,
    DEFAULT_VISUAL_AI_IMAGE_FORMAT,
    DEFAULT_VISUAL_AI_IMAGE_QUALITY,
    DEFAULT_VISUAL_AI_IMAGE_QUALITY_KEEP_IF_POSSIBLE,
    DEFAULT_VISUAL_AI_IMAGE_RESAMPLE_METHOD,
    DEFAULT_VISUAL_AI_IMAGE_SIZE,
    DEFAULT_VISUAL_AI_IMAGE_SUBSAMPLING,
    DEFAULT_VISUAL_AI_SHOULD_RESIZE,
    SUPPORTED_IMAGE_FORMATS,
)

try:
    from PIL import Image
except ImportError:
    msg = (
        "Image transformation operations require installation of datarobot library, "
        "with optional `images` dependency. To install library with image support"
        "please use `pip install datarobot[images]`"
    )
    raise ImportError(msg)


class ImageOptions(object):
    """
    Image options class. Class holds image options related to image resizing and image reformatting.

    should_resize: bool
        Whether input image should be resized to new dimensions.
    force_size: bool
        Whether the image size should fully match the new requested size. If the original
        and new image sizes have different aspect ratios, specifying True will force a resize
        to exactly match the requested size. This may break the aspect ratio of the original
        image. If False, the resize method modifies the image to contain a thumbnail version
        of itself, no larger than the given size, that preserves the image's aspect ratio.
    image_size: Tuple[int, int]
        New image size (width, height). Both values (width, height) should be specified and contain
        a positive value. Depending on the value of `force_size`, the image will be resized exactly
        to the given image size or will be resized into a thumbnail version of itself, no larger
        than the given size.
    image_format: enums.ImageFormat | str
        What image format will be used to save result image after transformations. For example
        (ImageFormat.JPEG, ImageFormat.PNG). Values supported are in line with values supported
        by DataRobot. If no format is specified by passing `None` value original image format
        will be preserved.
    image_quality: int or None
        The image quality used when saving image. When None is specified, a value will
        not be passed and Pillow library will use its default.
    resample_method: enum.ImageResampleMethod
        What resampling method should be used when resizing image.
    keep_quality: bool
        Whether the image quality is kept (when possible). If True, for JPEG images quality will
        be preserved. For other types, the value specified in `image_quality` will be used.
    """

    def __init__(
        self,
        should_resize=DEFAULT_VISUAL_AI_SHOULD_RESIZE,
        force_size=DEFAULT_VISUAL_AI_FORCE_SIZE,
        image_size=DEFAULT_VISUAL_AI_IMAGE_SIZE,
        image_format=DEFAULT_VISUAL_AI_IMAGE_FORMAT,
        image_quality=DEFAULT_VISUAL_AI_IMAGE_QUALITY,
        image_subsampling=DEFAULT_VISUAL_AI_IMAGE_SUBSAMPLING,
        resample_method=DEFAULT_VISUAL_AI_IMAGE_RESAMPLE_METHOD,
        keep_quality=DEFAULT_VISUAL_AI_IMAGE_QUALITY_KEEP_IF_POSSIBLE,
    ):
        self.should_resize = should_resize
        self.force_size = force_size
        self.image_size = image_size
        self.resample_method = resample_method
        self.image_quality = image_quality
        self.image_format = image_format
        self.image_quality = image_quality
        self.image_subsampling = image_subsampling
        self.keep_quality = keep_quality
        self._validate()

    def _validate(self):
        if self.should_resize is None:
            raise ValueError("Image transformation requires value `should_resize` parameter.")
        elif self.should_resize is True:
            if not self.image_size:
                raise ValueError("When resizing image `image_size` value is required.")
            width, height = self.image_size
            if width is None or width <= 0:
                raise ValueError("Image size width value should be positive number.")
            if height is None or height <= 0:
                raise ValueError("Image size height value should be positive number.")
        if self.image_format and self.image_format not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(
                "Invalid image_format value. Please specify `None` "
                "to preserve current image format or one of supported "
                "image formats: {}".format(SUPPORTED_IMAGE_FORMATS)
            )


def get_image_save_kwargs(image, image_options):
    """Return pillow save args depending on format and image options."""
    image_format = image_options.image_format if image_options.image_format else image.format
    kwargs = dict(compression="None", format=image_format)
    # add optional save parameters format dependant
    if image_format in {"JPEG", "PNG"}:
        kwargs["optimize"] = True
    if image_format == "JPEG":
        # keep can work only when source and target are jpeg
        if image_format == image.format and image_options.keep_quality:
            kwargs["quality"] = "keep"
        elif image_options.image_quality is not None:
            kwargs["quality"] = image_options.image_quality
    if image_options.image_subsampling is not None:
        kwargs["subsampling"] = image_options.image_subsampling
    return kwargs


def get_bytes_from_image(image, image_options):
    """
    Save PIL image with in specified format and with specified options and return image image_bytes.

    Parameters
    ----------
    image: PIL.Image
        Image object instance
    image_options: class ImageOptions
        Instance of class with image options

    Returns
    -------
    image_bytes representing Image
    """
    if image:
        bytes = io.BytesIO()
        image.save(fp=bytes, **get_image_save_kwargs(image, image_options))
        return bytes.getvalue()
    return None


def get_image_from_bytes(image_bytes):
    """
    Create PIL Image instance using input bytes.

    Parameters
    ----------
    image_bytes: bytes | BytesIO
        Image in a form of bytes.

    Returns
    -------
    PIL.Image instance
    """
    if image_bytes:
        if isinstance(image_bytes, bytes):
            image_bytes = io.BytesIO(image_bytes)
        image = Image.open(image_bytes)
        return image
    return None


def _scale_image_to_8bit_range(image):
    """
    This prevents a known bug of Pillow. When converting images, PIL clips the values.
    Thus, we have to manually scale the values, so they fit into 8 bit.
    https://github.com/python-pillow/Pillow/issues/2574
    """
    im_data = np.array(image)
    im_data = im_data * (2 ** 8 / im_data.max())
    image = Image.fromarray(im_data.astype(np.int32))
    return image


def format_image_bytes(image_bytes, image_options):
    """
    Format input image image_bytes and return reformatted image also in a form of image_bytes.

    Parameters
    ----------
    image_bytes: bytes
        Image in a form of image_bytes
    image_options : ImageOptions
        Class holding image formatting and image resize parameters

    Returns
    -------
    Image in a form of image_bytes
    """
    image = get_image_from_bytes(image_bytes)
    image_format = image.format
    # if image should be resized calculate new image size and resize original image
    if image_options.should_resize:
        if image_options.force_size:
            image = image.resize(
                size=image_options.image_size, resample=image_options.resample_method
            )
        else:
            image.thumbnail(size=image_options.image_size, resample=image_options.resample_method)

    if image.mode != "RGB":
        if image.mode == "I":
            image = _scale_image_to_8bit_range(image)
        image = image.convert("RGB")
        image.format = image_format

    # convert to target image format and return as image_bytes
    return get_bytes_from_image(image, image_options)
