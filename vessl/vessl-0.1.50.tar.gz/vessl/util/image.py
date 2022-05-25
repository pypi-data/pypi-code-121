import os
from typing import Optional, Union

import six

from vessl.util import logger
from vessl.util.common import generate_uuid, get_module
from vessl.util.constant import VESSL_MEDIA_PATH


class Image:
    def __init__(
        self,
        data: Union[str, "Image", "PIL.Image", "numpy.ndarray"],
        caption: Optional[str] = "",
        mode: Optional[str] = None,
    ):
        self._image = None
        self._caption = None
        self._mode = None
        self._path = None

        self._init_meta(caption, mode)
        self._init_image(data)
        self._save_image()

    def _init_meta(self, caption, mode):
        self._caption = caption
        self._mode = mode

        os.makedirs(VESSL_MEDIA_PATH, exist_ok=True)
        self._path = os.path.join(VESSL_MEDIA_PATH, generate_uuid() + ".png")

    def _init_image_from_path(self, data):
        pil_image = get_module(
            "PIL.Image",
            required='Pillow package is required. Run "pip install Pillow".',
        )
        self._image = pil_image.open(data)

    def _init_image_from_data(self, data):
        pil_image = get_module(
            "PIL.Image",
            required='Pillow package is required. Run "pip install Pillow".',
        )
        if Image.get_type_name(data).startswith("torch."):
            self._image = pil_image.fromarray(
                data.mul(255)
                .clamp(0, 255)
                .byte()
                .permute(1, 2, 0)
                .squeeze()
                .cpu()
                .numpy()
            )
        elif isinstance(data, pil_image.Image):
            self._image = data
        else:
            if hasattr(data, "numpy"):
                data = data.numpy()
            if data.ndim > 2:
                data = data.squeeze()
            self._image = pil_image.fromarray(
                Image.to_uint8(data),
                mode=self._mode,
            )

    def _init_image(self, data):
        if isinstance(data, Image):
            self._image = data._image
        elif isinstance(data, six.string_types):
            self._init_image_from_path(data)
        else:
            self._init_image_from_data(data)

    def _save_image(self):
        self._image.save(self._path)

    def flush(self):
        if os.path.isfile(self._path):
            os.remove(self._path)
        else:
            logger.error(f"Error: {self._path} file not found")

    @property
    def path(self):
        return self._path

    @property
    def caption(self):
        return self._caption

    @classmethod
    def get_type_name(cls, obj):
        type_name = obj.__class__.__module__ + "." + obj.__class__.__name__
        if type_name in ["builtins.module", "__builtin__.module"]:
            return obj.__name__
        else:
            return type_name

    @classmethod
    def to_uint8(cls, data):
        np = get_module(
            "numpy",
            required='numpy package is required. Run "pip install numpy"',
        )
        dmin = np.min(data)
        if dmin < 0:
            data = (data - np.min(data)) / np.ptp(data)
        if np.max(data) <= 1.0:
            data = (data * 255).astype(np.int32)

        return data.clip(0, 255).astype(np.uint8)
