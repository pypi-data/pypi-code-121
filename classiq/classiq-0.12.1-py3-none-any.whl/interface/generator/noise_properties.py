from typing import Optional

import pydantic

from classiq.interface.helpers.custom_pydantic_types import pydanticProbabilityFloat


class NoiseProperties(pydantic.BaseModel):

    measurement_bit_flip_probability: Optional[
        pydanticProbabilityFloat
    ] = pydantic.Field(
        default=None,
        description="Probability of measuring the wrong value for each qubit.",
    )
