from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Schema:
    feature_column_names: Optional[List[str]] = None
    numerical_feature_column_names: Optional[List[str]] = None
    categorical_feature_column_names: Optional[List[str]] = None
    timestamp_column_name: Optional[str] = None
    prediction_column_name: Optional[str] = None
    actual_column_name: Optional[str] = None
    prediction_probability_column_name: Optional[str] = None
