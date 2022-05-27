"""Column averaging algorithm."""
from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional

from marshmallow import fields
import numpy as np

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.algorithms.base import (
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerAlgorithm):
    """Modeller side of the ColumnAverage algorithm."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Simply returns results."""
        return results


class _WorkerSide(_BaseWorkerAlgorithm):
    """Worker side of the ColumnAverage algorithm."""

    def __init__(self, *, field: str, table_name: str, **kwargs: Any) -> None:
        self.datasource: _BaseSource
        self.field = field
        self.table_name = table_name
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.datasource = datasource

    def run(self) -> Dict[str, float]:
        """Returns the mean of the field in `_BaseSource` dataframe."""
        mean = np.mean(
            self.datasource.get_column(col_name=self.field, table_name=self.table_name)
        )
        return {"mean": float(mean)}


class ColumnAverage(_BaseAlgorithmFactory):
    """Simple algorithm for taking the arithmetic mean of a column in a table.

    Args:
        field: The name of the column to take the mean of.

    Attributes:
        name: The name of the algorithm.
        field: The name of the column to take the mean of.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "field": fields.Str(),
        "table_name": fields.Str(),
    }

    def __init__(self, *, field: str, table_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.field = field
        self.table_name = table_name

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ColumnAverage algorithm."""
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the ColumnAverage algorithm."""
        return _WorkerSide(field=self.field, table_name=self.table_name, **kwargs)
