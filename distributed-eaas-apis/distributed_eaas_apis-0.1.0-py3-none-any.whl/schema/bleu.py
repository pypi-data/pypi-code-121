"""Schema definition of the BLEU metric."""

from enum import Enum
from typing import final, List, Optional

from pydantic import BaseModel, Field


class TokenizeMethod(str, Enum):
    none = "none"
    zh = "zh"
    thirteen_a = "13a"
    intl = "intl"
    char = "char"
    ja_mecab = "ja-mecab"
    spm = "spm"


class SmoothMethod(str, Enum):
    floor = "floor"
    add_k = "add-k"
    exp = "exp"
    none = "none"


@final
class Config(BaseModel):
    """
    Configuration of the BLEU metric.
    Most of the settings are as-is from SacreBLEU.
    https://github.com/mjpost/sacrebleu/blob/master/sacrebleu/metrics/bleu.py
    """

    lowercase: bool = Field(False, description="If True, lowercased BLEU is computed.")
    force: bool = Field(False, description="Ignore data that looks already tokenized.")
    tokenize_method: Optional[TokenizeMethod] = Field(
        None,
        description="The tokenizer to use. If None, defaults to language-specific "
        "tokenizers with '13a' as the fallback default.",
    )
    smooth_method: SmoothMethod = Field(
        SmoothMethod.exp,
        description="The smoothing method to use ('floor', 'add-k', 'exp' or 'none').",
    )
    smooth_value: Optional[float] = Field(
        None,
        description="The smoothing value for `floor` and `add-k` methods. `None` falls "
        "back to default value.",
    )
    max_ngram_order: int = Field(
        4,
        description="If given, it overrides the maximum n-gram order (default: 4) when "
        "computing precisions.",
        ge=1,
    )
    effective_order: bool = Field(
        False,
        description="If `True`, stop including n-gram orders for which precision is 0. "
        "This should be `True`, if sentence-level BLEU will be computed.",
    )
    target_language: Optional[str] = Field(
        None,
        description="An optional language code to raise potential tokenizer warnings. "
        "Accepts ISO 639-1 or 639-3 codes.",
    )


@final
class Example(BaseModel):
    """Example for calculating BLEU. Can use one or multiple references."""

    references: List[str] = Field(description="List of reference sentences.")
    hypothesis: str = Field(description="Hypothesis sentence.")


@final
class Statistics(BaseModel):
    """Statistics of the BLEU metric."""

    hypothesis_length: int = Field(0, description="Length of the hypothesis.", ge=0)
    reference_length: int = Field(0, description="Length of the reference.", ge=0)
    correct: List[int] = Field([], description="Number correct for each n-gram length.")
    total: List[int] = Field([], description="Number total for each n-gram length.")


@final
class Summary(BaseModel):
    """Summary of the BLEU metric."""

    bleu: float = Field(description="BLEU score", ge=0.0, le=1.0)
    ratio: float = Field(description="Length ratio", ge=0.0)
    ngram_precision: List[float] = Field(description="N-gram precisions")
