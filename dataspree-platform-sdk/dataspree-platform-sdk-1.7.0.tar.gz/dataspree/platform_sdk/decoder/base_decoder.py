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

from abc import ABC, abstractmethod

from typing import List, Tuple, Optional, Dict, Any

import numpy as np


class BaseDecoder(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def __call__(self, data: bytes) -> Tuple[np.ndarray, Optional[Dict[str, Any]]]:
        """
        Stub for implementing the decoding procedure
        called:
        >>> decoder = BaseDecoder()
        >>> decoder(encoded_bytes)

        :return Decoded data, metainformation
        """
        pass

    @staticmethod
    @abstractmethod
    def get_file_extensions() -> List[str]:
        """
        Stub for returning allowed file endings
        """
        pass

    def __reduce__(self) -> Tuple:
        return BaseDecoder, tuple()
