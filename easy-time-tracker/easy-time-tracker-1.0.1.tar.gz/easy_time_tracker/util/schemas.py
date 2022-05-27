"""
Data schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class StartTimeRecordSchema(BaseModel):  # pylint: disable=too-few-public-methods
    """Class schema to start a record"""
    description: str
    people: list
    time_zone: str
    start_time: str


class EndTimeRecordSchema(StartTimeRecordSchema):  # pylint: disable=too-few-public-methods
    """Class schema to end a record"""
    end_time: str
    ending_comments: Optional[str] = Field(default='no comments added')
    total_time_worked: str


class CompletedTimeRecordsSchema(BaseModel):  # pylint: disable=too-few-public-methods
    """Class schema for records archive"""
    records: List[EndTimeRecordSchema]
