"""mfire.data module

This module handles everything related to the Data Handling :
    - Data Preprocessing
    - Aggregation
"""
from mfire.data.data_preprocessor import DataPreprocessor
from mfire.data.aggregator import Aggregator, AGGREGATION_CATALOG

__all__ = ["DataPreprocessor", "Aggregator", "AGGREGATION_CATALOG"]
