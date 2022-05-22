from typing import List, Optional

import pydantic

from classiq.interface.helpers.custom_pydantic_types import pydanticProbabilityFloat


class ModelParams(pydantic.BaseModel):
    loss: List[int] = pydantic.Field(
        description="List of ints signifying loss per asset"
    )
    min_loss: Optional[int] = pydantic.Field(
        description="Minimum possible loss for the model "
    )


class GaussianModelInput(ModelParams):
    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits represent"
        "the latent normal random variable Z (Resolution of "
        "the random variable Z)."
    )
    normal_max_value: float = pydantic.Field(
        description="Min/max value to truncate the " "latent normal random variable Z"
    )
    default_probabilities: List[pydanticProbabilityFloat] = pydantic.Field(
        description="default probabilities for each asset"
    )

    rhos: List[pydantic.PositiveFloat] = pydantic.Field(
        description="Sensitivities of default probability of assets "
        "with respect to Z (1/sigma(Z))"
    )

    @property
    def num_model_qubits(self):
        return len(self.rhos)

    @property
    def distribution_range(self):
        return [0, sum(self.loss)]
