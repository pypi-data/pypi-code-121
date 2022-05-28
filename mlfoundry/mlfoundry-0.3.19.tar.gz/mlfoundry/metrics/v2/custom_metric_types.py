import typing

from pydantic import BaseModel, Field


class RocCurve(BaseModel):
    fpr: typing.List[float]
    tpr: typing.List[float]
    thresholds: typing.List[float]


class PrCurve(BaseModel):
    precision: typing.List[float]
    recall: typing.List[float]
    thresholds: typing.List[float]


class ConfusionMatrix(BaseModel):
    class_names: typing.List[str]
    matrix: typing.List[typing.List[float]]


class ClassificationReport(BaseModel):
    precision: float
    recall: float
    f1_score: float = Field(None, alias="f1-score")
    support: float
