"""Test MessageService federated transport layer with LightGBM models."""
import asyncio
from typing import Callable
from unittest.mock import Mock

import pytest
from pytest import fixture

from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from tests.utils.helper import (
    AUC_THRESHOLD,
    backend_test,
    create_local_modeller_and_workers,
    integration_test,
)


@integration_test
class TestMessageServiceUsage:
    """Tests for Message Service federated transport layer for training jobs."""

    @fixture
    def mock_get_pod_public_keys(
        self, apply_mock_get_pod_public_keys: Callable[[str], Mock]
    ) -> Mock:
        """Mocks out get_pod_public_keys function in modeller.py."""
        return apply_mock_get_pod_public_keys(
            "bitfount.federated.modeller._get_pod_public_keys"
        )

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    @backend_test
    async def test_classifier_runs(
        self,
        mock_get_pod_public_keys: Mock,
        mock_message_aes_decryption: Mock,
        mock_message_aes_encryption: Mock,
        mock_rsa_encryption: Mock,
        mock_rsa_sign_message: Mock,
    ) -> None:
        """Tests that a Logistic Regression classifier runs."""
        modeller, workers = create_local_modeller_and_workers(
            model_name="LGBMRandomForestClassifier",
            protocol_name="ResultsOnly",
            algorithm_name="ModelTrainingAndEvaluation",
        )

        modeller_results, *_ = await asyncio.gather(
            modeller.run_async([worker.mailbox.pod_identifier for worker in workers]),
            *[_run_func_and_listen_to_mailbox(w.run(), w.mailbox) for w in workers]
        )

        for result in modeller_results:
            assert result is not None
            assert isinstance(result, dict)
            auc = result["AUC"]
            assert auc > AUC_THRESHOLD
