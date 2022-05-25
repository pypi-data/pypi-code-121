#  Copyright 2022 Data Spree GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
from enum import Enum
from typing import Tuple, Dict, Any, List, Optional

import cv2
import numpy as np
from numpy.lib.recfunctions import unstructured_to_structured
from PIL import ExifTags, Image

from dataspree.platform_sdk.decoder.base_decoder import BaseDecoder


class ReadingMode(Enum):
    GRAYSCALE = 1
    RGB = 2
    RGBA = 3
    ANY = 4


class OpencvDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__()

        self.exif_orientation_tag = None
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                self.exif_orientation_tag = orientation
                break

    def __call__(self, data: bytes) -> Tuple[np.ndarray, Optional[Dict[str, Any]]]:
        image = cv2.imdecode(np.asarray(bytearray(data), dtype=np.uint8), cv2.IMREAD_UNCHANGED)

        # rotate the image according to the exif orientation
        if self.exif_orientation_tag is not None:
            # unfortunately, opencv does not expose the exif flags, so that we open the image with pillow
            # fortunately, pillow opens images in a lazy fashion
            image_pil = Image.open(io.BytesIO(data))
            if hasattr(image_pil, '_getexif'):
                exif = image_pil._getexif()
                if exif is not None:
                    exif = dict(exif.items())
                    if self.exif_orientation_tag in exif:
                        if exif[self.exif_orientation_tag] == 3:
                            image = cv2.rotate(image, cv2.ROTATE_180)
                        elif exif[self.exif_orientation_tag] == 6:
                            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                        elif exif[self.exif_orientation_tag] == 8:
                            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        image = self.create_sturctured_array(image)

        return image, dict()

    def __reduce__(self) -> Tuple:
        return OpencvDecoder, tuple()

    @staticmethod
    def get_file_extensions() -> List[str]:
        return ['bmp', 'dib', 'jpeg', 'jpg', 'jpe', 'jp2', 'png', 'pdm', 'pgm', 'ppm', 'sr', 'ras', 'tiff', 'tif']

    @staticmethod
    def create_sturctured_array(image: np.ndarray, n_chans = None) -> np.ndarray:
        ### FIXME : remove n_chans kwarg -> bad quick fix
        ### TODO: check if image is valid (has hight/widht, shape-len is 2 or 3)
        if n_chans is not None:
            n_channels = n_chans
        else:
            n_channels = image.shape[-1] if len(image.shape) == 3 else 1
            if len(image.shape) == 2:
                image = image[:,:,True]
        if n_channels == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif n_channels == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)

        if n_channels == 1:
            image = unstructured_to_structured(image, np.dtype([('gray', image.dtype)]))
        elif n_channels == 3:
            image = unstructured_to_structured(image, np.dtype(
                [('red', image.dtype), ('green', image.dtype), ('blue', image.dtype)]))
        elif n_channels == 4:
            image = unstructured_to_structured(image, np.dtype(
                [('red', image.dtype), ('green', image.dtype), ('blue', image.dtype), ('alpha', image.dtype)]))
        else:
            raise ValueError(f'Cannot decode channel semantics of {image.shape[-1]} channel image.')
        return image