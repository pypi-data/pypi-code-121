from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InsightCreate(BaseModel):
    name: Optional[str]
    dataset_id: int = Field(alias='datasetId')
    transform_id: int = Field(alias='transformId')
    transform_arguments: Dict[str, Any] = Field(alias='transformArguments')
    dw_table_id: int = Field(alias='dwTableId')

    class Config:
        allow_population_by_field_name = True


class Insight(InsightCreate):
    id: int
