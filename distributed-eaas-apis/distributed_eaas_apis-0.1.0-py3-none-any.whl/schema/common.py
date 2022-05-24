"""Common schema definitions for metrics."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar  # noqa: PEA001

from pydantic import BaseModel, constr, ConstrainedStr, Field
from pydantic.generics import GenericModel

ConfigT = TypeVar("ConfigT")
ExampleT = TypeVar("ExampleT")
StatisticsT = TypeVar("StatisticsT")
SummaryT = TypeVar("SummaryT")


# Dash-case lowercased alphanumerics, starting with an alphabet.
MetricName: ConstrainedStr = constr(regex=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class Metadata(BaseModel):
    """Metadata of metrics."""

    # Name of the
    name: MetricName = Field(description="Name of the metric.")
    description: str = Field(description="Description of the metric.")
    version: str = Field(description="Semantic version of the metric.")


class ProcessRequest(GenericModel, Generic[ConfigT, ExampleT, StatisticsT]):
    """Request information of metrics."""

    config: Optional[ConfigT] = Field(None, description="Configurations of the metric.")
    examples: List[ExampleT] = Field(
        description="List of new examples to be processed."
    )
    statistics: Optional[StatisticsT] = Field(
        None,
        description=(
            "Statistics of previous calls. If provided, it is aggregated additionally "
            "to the `aggregated` result in `ProcessResponse`."
        ),
    )


class MetricResult(GenericModel, Generic[StatisticsT, SummaryT]):
    """Information of individual scores for each example or aggregated score."""

    statistics: StatisticsT = Field(description="Statistics of this result.")
    summary: SummaryT = Field(description="Summary of this result.")


class ProcessResponse(GenericModel, Generic[StatisticsT, SummaryT]):
    """Response information of metrics."""

    examples: List[MetricResult[StatisticsT, SummaryT]] = Field(
        description=(
            "Example-wise results. The order of the member corresponds to that in "
            "`ProcessRequest`."
        )
    )
    aggregated: MetricResult[StatisticsT, SummaryT] = Field(
        description="Aggregated result."
    )
