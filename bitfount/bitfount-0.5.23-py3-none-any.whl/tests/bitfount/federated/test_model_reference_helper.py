"""Tests the model reference helper module."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_asyncio import fixture
from pytest_mock import MockerFixture

from bitfount import BitfountModelReference, BitfountSchema, DataStructure, _Modeller
from bitfount.federated.model_reference_helper import (
    create_and_run_modeller_from_bf_model_ref,
)
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils.helper import create_datastructure, unit_test


@fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@fixture
def model_ref(
    bitfount_model_correct_structure: str,
    datastructure: DataStructure,
    tmp_path: Path,
) -> BitfountModelReference:
    """Fixture for BitfountModelReference."""
    model_file = tmp_path / "MyModel.py"
    model_file.touch()
    model_file.write_text(bitfount_model_correct_structure)
    hub_mock = MagicMock()
    hub_mock.send_model.return_value = True
    # Create model to test
    return BitfountModelReference(
        username="test",
        datastructure=datastructure,
        schema=BitfountSchema(),
        model_ref=model_file,
        hub=hub_mock,
        hyperparameters={"epochs": 1},
    )


@unit_test
def test_create_and_run_modeller_from_bf_model_ref(
    mocker: MockerFixture,
    model_ref: BitfountModelReference,
    tmp_path: Path,
) -> None:
    """Tests the helper function for custom models.

    Checks that the create_and_run_modeller_from_bf_model_ref method creates
    correct instances and runs the modeller correctly.
    """
    # Patch out the modeller's run method
    mock_modeller_run_method = mocker.patch.object(_Modeller, "run")

    # Run method
    pod_identifiers = ["bitfount/adult"]
    create_and_run_modeller_from_bf_model_ref(
        model_ref,
        pod_identifiers=pod_identifiers,
        private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
    )
    # Check run method was called correctly
    mock_modeller_run_method.assert_called_once_with(pod_identifiers, model_out=None)


@unit_test
def test_create_and_run_modeller_from_bf_model_ref_error_steps_epochs(
    model_ref: BitfountModelReference,
) -> None:
    """Test helper function raises error with both model epochs and steps."""
    model_ref.hyperparameters = {"epochs": 1, "steps": 2}
    pod_identifiers = ["bitfount/adult"]

    with pytest.raises(ValueError):
        create_and_run_modeller_from_bf_model_ref(
            model_ref, pod_identifiers=pod_identifiers
        )


@unit_test
def test_create_and_run_modeller_from_bf_model_ref_error_no_steps_epochs(
    model_ref: BitfountModelReference,
) -> None:
    """Test helper function raises error with none of model epochs and steps given."""
    model_ref.hyperparameters = {}
    pod_identifiers = ["bitfount/adult"]

    with pytest.raises(ValueError):
        create_and_run_modeller_from_bf_model_ref(
            model_ref, pod_identifiers=pod_identifiers
        )


@unit_test
def test_modeller_run_result_false_returns_none(
    mocker: MockerFixture,
    model_ref: BitfountModelReference,
) -> None:
    """Test that result is None when modeller returns False."""
    pod_identifiers = ["bitfount/adult"]
    # Patch out the modeller's run method
    with mocker.patch.object(_Modeller, "run", return_value=False):
        # Run method
        result = create_and_run_modeller_from_bf_model_ref(
            model_ref,
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )
        assert result is None
