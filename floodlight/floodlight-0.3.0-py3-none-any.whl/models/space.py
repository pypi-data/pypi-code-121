from typing import Tuple

import numpy as np
from scipy.spatial.distance import cdist

from floodlight import Pitch, XY
from floodlight.core.property import PlayerProperty
from floodlight.utils.types import Numeric
from floodlight.models.base import BaseModel


class VoronoiModel(BaseModel):
    def __init__(self, pitch):
        super().__init__(pitch)

        # initialize instance attributes
        self.mesh_ = None


    def _create_mesh(
            self,
            xlim: Tuple[Numeric, Numeric],
            ylim: Tuple[Numeric, Numeric],
            step_size: int,
    ):
        # init pitch
        mesh = np.meshgrid()

    def fit(self, xy1: XY, xy2: XY) -> None:
        pass



