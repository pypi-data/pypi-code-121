#  Copyright 2021 Data Spree GmbH
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

import logging
from enum import Enum
from typing import Tuple, Dict, Any, List

import numpy as np
from PIL import ExifTags

from dataspree.platform_sdk.decoder.base_decoder import BaseDecoder
from dataspree.platform_sdk.decoder.serializer import load_pcd, load_ply

logger = logging.getLogger(__name__)


class ReadingMode(Enum):
    GRAYSCALE = 1
    RGB = 2
    RGBA = 3
    ANY = 4


class PcdDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__()

        # TODO: Document me!
        self.exif_orientation_tag = None
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                self.exif_orientation_tag = orientation
                break

    def __call__(self, data) -> Tuple[np.ndarray, Dict[str, Any]]:
        return load_pcd(data)

    def __reduce__(self) -> Tuple:
        return PcdDecoder, tuple()

    @staticmethod
    def get_file_extensions() -> List[str]:
        return ['pcd']


class PlyDecoder(PcdDecoder):
    # TODO: Test me!
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, data) -> Tuple[np.ndarray, Dict[str, Any]]:
        return load_ply(data)

    def __reduce__(self) -> Tuple:
        return PlyDecoder, tuple()

    @staticmethod
    def get_file_extensions() -> List[str]:
        return ['ply']
