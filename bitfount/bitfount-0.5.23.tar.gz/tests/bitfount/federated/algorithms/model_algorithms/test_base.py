"""Tests for base model algorithms module."""

from typing import Optional
from unittest.mock import Mock

import pytest

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseWorkerModelAlgorithm,
)
from bitfount.types import _SerializedWeights
from tests.utils.helper import create_datasource, unit_test


@unit_test
class TestBase:
    """Test base model algorithms module."""

    @pytest.fixture
    def datasource(self) -> _BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    @pytest.mark.parametrize("model_params", [{"param": [1]}, None])
    def test_base_worker_initialise(
        self, datasource: _BaseSource, model_params: Optional[_SerializedWeights]
    ) -> None:
        """Test initialise updates model parameters on worker side."""
        model = Mock(create_autospec=True)
        base = _BaseWorkerModelAlgorithm(model=model)
        base.initialise(datasource, model_params=model_params)
        if model_params:
            base.model.update_params.assert_called_once()  # type: ignore[attr-defined]  # Reason: model is a mock  # noqa: B950
        else:
            base.model.update_params.assert_not_called()  # type: ignore[attr-defined]  # Reason: model is a mock  # noqa: B950
