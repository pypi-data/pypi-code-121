"""Tests the gradients of our federated models match the local ones."""
import logging
import time
from typing import cast
from unittest.mock import AsyncMock

from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
import pytest
import torch

from bitfount import (
    BitfountSchema,
    FederatedAveraging,
    FederatedModelTraining,
    Optimizer,
    Pod,
)
from bitfount.backends.pytorch import PyTorchTabularClassifier
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.federated.helper import _create_aggregator
from bitfount.runners.config_schemas import PodDataConfig
from tests.utils.helper import (
    backend_test,
    create_dataset,
    create_datastructure,
    integration_test,
)

logger = logging.getLogger(__name__)


@backend_test
@integration_test
class TestGradients:
    """End-to-end tests using the Adult dataset."""

    @pytest.fixture(autouse=True)
    def bitfount_env(self, monkeypatch: MonkeyPatch) -> None:
        """Set BITFOUNT_ENVIRONMENT env var to 'staging'."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")

    def test_gradients_pytorchtab(
        self,
    ) -> None:
        """Tests local vs remote gradients for tabular classifier."""
        # Setup the data; The same will be used for both federated and local models
        dataset = cast(pd.DataFrame, create_dataset().head(100))

        datastructure = create_datastructure()
        datasource = DataFrameSource(dataset, ignore_cols="Date")
        schema = BitfountSchema()
        schema.add_datasource_tables(
            datasource,
            force_stypes={"test_table": {"categorical": ["TARGET"]}},
            table_name="test_table",
        )
        # Setup the pod.
        suffix = str(int(time.time()))
        pod_name = "pod1" + suffix
        bitfounthub = AsyncMock()
        bitfounthub.session.username = "username"
        pod = Pod(
            name=pod_name,
            datasource=datasource,
            data_config=PodDataConfig(
                ignore_cols=["Date"],
                force_stypes={pod_name: {"categorical": ["TARGET"]}},
            ),
            bitfounthub=bitfounthub,
        )

        # Setup the federated model, algorithm, aggregator and protocol
        fed_model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            seed=100,
            epochs=1,
            batch_size=10,
            optimizer=Optimizer(name="SGD", params={"lr": 1.0}),
        )
        algorithm = FederatedModelTraining(model=fed_model)
        aggregator = _create_aggregator(
            secure_aggregation=False,
        )
        protocol = FederatedAveraging(
            algorithm=algorithm,
            aggregator=aggregator,
            epochs_between_parameter_updates=1,
            steps_between_parameter_updates=None,
        )

        # Setup the modeller
        mod_mailbox = AsyncMock()

        # Start the protocol on the modeller side to get the initial model params
        mod_protocol = protocol.modeller(mailbox=mod_mailbox)
        mod_protocol.algorithm.initialise()
        params = mod_protocol.algorithm.run(update=None)

        # Worker side of the protocol
        worker = protocol.worker(mailbox=AsyncMock(), hub=pod._hub)

        # The following code repeats what is in the worker side of the protocol;
        # extracted here to avoid async calls and to be able to extract the
        # gradient from the trained federated model.
        worker.algorithm.initialise(datasource=pod.datasource)
        num_federated_iterations = worker.get_num_federated_iterations()
        for i in range(1, num_federated_iterations + 1):
            if worker.algorithm.epochs:
                logger.info(f"Federated Epoch {i}")
                iterations = worker.epochs_between_parameter_updates
            else:
                logger.info(f"Federated Step {i}")
                iterations = worker.steps_between_parameter_updates
            iterations = cast(int, iterations)
            worker.algorithm.run(pod.datasource, params, iterations)

        # Train a local model.
        local_model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            seed=100,
            epochs=1,
            batch_size=10,
            optimizer=Optimizer(name="SGD", params={"lr": 1.0}),
        )
        local_model.fit(datasource)

        # Check that the gradients match
        for i in range(len(local_model._training_epoch_end_gradients)):
            assert torch.allclose(
                local_model._training_epoch_end_gradients[i],
                worker.algorithm.model._training_epoch_end_gradients[i],  # type: ignore[attr-defined] # reason: see below # noqa: B950
            )
        # mypy error: we defined the worker using a model,
        # and the purpose of the test is to test the gradients
