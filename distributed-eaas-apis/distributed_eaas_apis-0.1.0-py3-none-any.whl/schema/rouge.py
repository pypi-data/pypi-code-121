"""Schema definition of the ROUGE metric."""

from enum import Enum
from typing import final, List, Optional

from pydantic import BaseModel, Field


@final
class Variety(str, Enum):
    """Variation of scoring method."""

    ROUGE_1 = "rouge1"
    ROUGE_2 = "rouge2"
    ROUGE_L = "rougeL"


@final
class MultiReferenceAggregation(str, Enum):
    """Aggregation method of multi-reference scores."""

    MAX = "max"
    MEAN = "mean"


@final
class Config(BaseModel):
    """Configurations of the ROUGE metric."""

    variety: Optional[Variety] = Field(
        None,
        description=(
            "The variation of the metric, msut be either 'rouge1', 'rouge2, or "
            "'rougeL'. Defaults to 'rouge1'."
        ),
    )

    multi_reference_aggregation: Optional[MultiReferenceAggregation] = Field(
        None,
        description=(
            "Aggregation method of multi-reference scores, must be either 'max' or "
            "'mean'. Defaults to 'max'."
        ),
    )

    use_stemmer: Optional[bool] = Field(
        None,
        description="Whether to use the internal stemmer or not. Defaults to 'True'",
    )

    target_language: Optional[str] = Field(
        None,
        description=(
            "ISO 639-1 language code of the hypotheses/references. Currently the metric"
            "supports only 'en'. Defaults to 'en'."
        ),
    )


@final
class Example(BaseModel):
    """Example of the ROUGE metric."""

    references: List[str] = Field(description="List of reference sentences.")
    hypothesis: str = Field(description="Hypothesis sentence.")


# TODO(odashi): Add fine-grained statistics.
@final
class Statistics(BaseModel):
    """Statistics of the ROUGE metric."""

    sum_score: float = Field(0, description="Sum of all scores calculated.", ge=0.0)
    num_examples: int = Field(0, description="Number of examples.", ge=0)


# TODO(odashi): Add fine-grained summaries.
@final
class Summary(BaseModel):
    """Summary of the ROUGE metric."""

    score: float = Field(0, description="Mean of the scores of all examples.", ge=0.0)
