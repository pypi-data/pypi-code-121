"""Tests for PyTorch-backed models."""
from __future__ import annotations

from functools import partial
import logging
import os
from pathlib import Path
import re
from typing import Any, Dict, List, MutableMapping, Optional, cast
from unittest.mock import Mock, create_autospec

from _pytest.logging import LogCaptureFixture
import numpy as np
from opacus import PrivacyEngine
from opacus.validators import ModuleValidator
from opacus.validators.errors import UnsupportedModuleError
import pandas as pd
import py
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from pytorch_lightning import Trainer as LightningTrainer
from pytorch_lightning.loggers import (
    MLFlowLogger,
    NeptuneLogger,
    TensorBoardLogger,
    TestTubeLogger,
    WandbLogger,
)
from pytorch_lightning.loggers import CSVLogger
from pytorch_lightning.loggers import LightningLoggerBase as LightningLoggers
from sklearn.metrics import roc_auc_score
import sqlalchemy
import torch
from torch import nn as nn
from torch.nn import CrossEntropyLoss, Linear, ReLU
import torch_optimizer

from bitfount.backends.pytorch.data.dataloaders import _PyTorchBitfountDataLoader
from bitfount.backends.pytorch.models.base_models import BasePyTorchModel
from bitfount.backends.pytorch.models.models import (
    PyTorchImageClassifier,
    PyTorchLogisticRegressionClassifier,
    PyTorchTabularClassifier,
    TabNetClassifier,
)
from bitfount.data.databunch import _BitfountDataBunch
from bitfount.data.datasets import _BitfountDataset
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasplitters import PercentageSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema, TableSchema
from bitfount.data.types import DataSplit, SemanticType, _SemanticTypeValue
from bitfount.data.utils import DatabaseConnection
from bitfount.federated.modeller import _Modeller
from bitfount.federated.privacy.differential import DPModellerConfig
from bitfount.metrics import (
    BINARY_CLASSIFICATION_METRICS,
    MULTICLASS_CLASSIFICATION_METRICS,
    ClassificationMetric,
    MetricCollection,
)
from bitfount.models.base_models import (
    MAIN_MODEL_REGISTRY,
    CNNModelStructure,
    FeedForwardModelStructure,
    LoggerConfig,
    ModelContext,
    NeuralNetworkModelStructure,
    NeuralNetworkPredefinedModel,
    Optimizer,
    Scheduler,
)
from bitfount.schemas.utils import bf_dump, bf_load
from bitfount.types import _StrAnyDict
from bitfount.utils import _add_this_to_list
from tests.bitfount import TEST_SECURITY_FILES
from tests.bitfount.models.test_models import SERIALIZED_MODEL_NAME
from tests.utils.helper import (
    AUC_THRESHOLD,
    TABLE_NAME,
    assert_results,
    backend_test,
    create_dataset,
    create_datasource,
    create_datastructure,
    create_query_datastructure,
    create_schema,
    get_datastructure_and_datasource,
    get_debug_logs,
    get_info_logs,
    get_warning_logs,
    integration_test,
    unit_test,
)


def assert_vars_equal(vars_original: _StrAnyDict, vars_copy: _StrAnyDict) -> None:
    """Asserts both vars() are equal."""
    for variable, value in vars_original.items():
        if not isinstance(
            value,
            (
                LightningTrainer,
                LightningLoggers,
                DataStructure,
                BitfountSchema,
            ),
        ) and variable not in ["opt_func", "scheduler_func"]:
            assert value == vars_copy[variable]
        else:
            if isinstance(value, DataStructure):
                assert value.target == vars_copy[variable].target
            elif variable == "opt_func" and value is not None:
                assert issubclass(
                    value.func, (torch.optim.Optimizer, torch_optimizer.Optimizer)
                )
                assert value.func == vars_copy[variable].func
                assert value.keywords == vars_copy[variable].keywords
            elif variable == "_scheduler_func" and value is not None:
                assert issubclass(value.func, torch.optim.lr_scheduler._LRScheduler)
                assert value.func == vars_copy[variable].func
                assert value.keywords == vars_copy[variable].keywords


@pytest.fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@pytest.fixture
def datasource() -> _BaseSource:
    """Fixture for datasource."""
    return create_datasource(classification=True)


@pytest.fixture
def schema() -> BitfountSchema:
    """Fixture for schema."""
    return create_schema(classification=True)


@pytest.fixture
def mock_databunch(mocker: MockerFixture) -> None:
    """Mocked _BitfountDataBunch."""
    mocker.patch.object(_BitfountDataBunch, "_create_datasets", autospec=True)


@pytest.fixture
def query_datastructure() -> DataStructure:
    """Fixture for datastructure containing query."""
    return create_query_datastructure()


@backend_test
class TestPyTorchModel:
    """Test BasePyTorchModel class and all subclasses."""

    @unit_test
    def test_training_steps(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test that training works with steps instead of epochs."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        assert model._pl_trainer.max_epochs == -1
        assert model._pl_trainer.max_steps == 10
        model.fit(datasource)

    @unit_test
    @pytest.mark.parametrize(
        "epochs, steps",
        [(1, None), (None, 1), (None, 1000)],
    )
    def test_trainer_validate_method_is_called_when_training_with_steps(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        epochs: Optional[int],
        mocker: MockerFixture,
        schema: BitfountSchema,
        steps: Optional[int],
    ) -> None:
        """Tests that trainer `validate` method is called when training with steps.

        This is to ensure we always have validation results even if we are not training
        for a fixed number of epochs.
        """
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            steps=steps,
            epochs=epochs,
        )
        # `autospec` set to True causes a RunTime error due to dynamic properties on the
        # trainer.
        mock_trainer = mocker.patch.object(model, "_pl_trainer")

        def mock_fit_validate(model: BasePyTorchModel) -> None:
            """Mock method for `fit` and `validate` Trainer methods.

            Simply appends some fake validation results to `model_validation_results`.
            """
            model._validation_results.append({"test_metric": "test_value"})

        mock_trainer.fit.side_effect = mock_fit_validate
        mock_trainer.validate.side_effect = mock_fit_validate

        final_results = model.fit(datasource)
        mock_trainer.fit.assert_called_once()
        if steps:
            mock_trainer.validate.assert_called_once()
        else:
            mock_trainer.validate.assert_not_called()

        assert final_results == {"test_metric": "test_value"}

    @integration_test
    @pytest.mark.parametrize(
        "epochs, steps",
        [(2, None), (None, 1), (None, 17)],
    )
    def test_validation_always_run_at_end_of_training(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        epochs: Optional[int],
        schema: BitfountSchema,
        steps: Optional[int],
    ) -> None:
        """Tests that validation is always run at the end of training.

        Regardless of whether training is specified in terms of steps or epochs.

        Note: 17 steps with a batch size of 256 is greater than the number of batches
        in the dataset to ensure we go past one epoch.
        """
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            steps=steps,
            epochs=epochs,
            batch_size=256,
        )
        final_results = model.fit(datasource)
        assert isinstance(final_results, dict)

        if epochs:
            assert len(model._validation_results) == epochs
        elif steps:
            assert len(model._validation_results) == steps // len(model.train_dl) + 1

    @unit_test
    def test_classifier_has_n_classes_after_init_modeller_context(
        self, datastructure: DataStructure, schema: BitfountSchema
    ) -> None:
        """Test that n_classes is set during initialise_model in modeller context."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=schema, steps=10
        )
        assert not hasattr(model, "n_classes")
        model.initialise_model(context=ModelContext.MODELLER)
        assert model.n_classes == 2

    @integration_test
    def test_model_init_with_db_query(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        query_datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests that model is initialised with a query datastructure."""
        model = PyTorchTabularClassifier(
            datastructure=query_datastructure, schema=schema, steps=2
        )
        db_datasource = DatabaseSource(DatabaseConnection(db_session))
        assert isinstance(query_datastructure.query, str)
        db_datasource.datastructure_query = query_datastructure.query
        expected_schema = query_datastructure._override_schema(db_datasource)
        model.initialise_model(db_datasource)
        assert model._databunch is not None
        assert model.n_classes == 2
        assert model._databunch.schema == expected_schema

    @unit_test
    @pytest.mark.parametrize(
        "epochs, steps, value_error",
        [
            (0, 0, True),
            (1, 10, True),
            (None, None, True),
            (None, 1, False),
            (1, None, False),
            (None, 0, False),
        ],
    )
    def test_epochs_steps_value_error_raised_correctly(
        self,
        datastructure: DataStructure,
        epochs: int,
        steps: int,
        value_error: ValueError,
    ) -> None:
        """Ensure steps/epochs logic is correct in NeuralNetworkMixIn."""
        if value_error:
            with pytest.raises(ValueError):
                PyTorchTabularClassifier(
                    datastructure=datastructure,
                    schema=BitfountSchema(),
                    steps=steps,
                    epochs=epochs,
                )
        else:
            PyTorchTabularClassifier(
                datastructure=datastructure,
                schema=BitfountSchema(),
                steps=steps,
                epochs=epochs,
            )

    @unit_test
    @pytest.mark.parametrize("steps", [5, 100])
    def test_stepwise_fit_remembers_batch_number_after_reset(
        self, datasource: DataFrameSource, datastructure: DataStructure, steps: int
    ) -> None:
        """Tests that the model remembers the batch number in between `fit` calls.

        This allows us to call `fit` multiple times on the same model without training
        on the same batches as before.
        """

        class _PyTorchTabularClassifier(PyTorchTabularClassifier):
            batch_indices_trained_on = []

            def on_train_batch_end(self, outputs, batch, batch_idx, dataloader_idx):  # type: ignore[no-untyped-def] # Reason: just a test method # noqa: B950
                """Hook called at the end of each batch training.

                Implementing this allows us to keep track of batches that were actually
                trained on. If `outputs` is empty, then the batch was skipped.
                """
                if outputs:
                    self.batch_indices_trained_on.append(batch_idx)

        model = _PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=steps,
            batch_size=32,
        )
        model.fit(datasource)
        # index starts from 0
        assert model._pl_trainer.fit_loop.batch_idx == steps - 1
        assert model._total_num_batches_trained == steps

        model.reset_trainer()
        model.fit(datasource)
        # We take the modulo of batches in an epoch to ensure the calculation works
        # even if the number of batches goes past how many there are in an epoch
        assert model._pl_trainer.fit_loop.batch_idx == (
            ((steps * 2) - 1) % len(model.train_dl)
        )  # index starts from 0
        assert model._total_num_batches_trained == steps * 2

        # The batch indices trained on should go up sequentially and smoothly indicating
        # that the batches are going in order and that no batches are skipped/repeated
        assert model.batch_indices_trained_on == [
            i % len(model.train_dl) for i in range(steps * 2)
        ]

    @integration_test
    def test_transfer_learning(self) -> None:
        """Tests transfer learning works."""
        datastructure, datasource = get_datastructure_and_datasource(
            classification=True, loss_weights=True
        )
        lr = 0.01
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=32,
            lr=lr,
        )
        neural_network.fit(datasource)
        # divide learning rate by 10
        neural_network._opt_func = partial(neural_network._opt_func, lr=lr * 0.1)
        neural_network.fit(datasource)  # fine tune pre-trained model
        assert_results(model=neural_network)

    @integration_test
    def test_multitask_transfer_learning(self) -> None:
        """Tests multitask training works."""
        lr = 0.01
        datastructure, datasource = get_datastructure_and_datasource(
            classification=True, multihead=True, multihead_size=2, loss_weights=True
        )
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=32,
            optimizer_func=torch.optim.AdamW,
            optimizer_params={"lr": lr},
        )

        neural_network.fit(datasource)
        # divide learning rate by 10
        neural_network._opt_func = partial(neural_network._opt_func, lr=lr * 0.1)
        neural_network.fit(datasource)  # fine tune pre-trained model
        assert_results(model=neural_network)

    @integration_test
    def test_classification(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests Tabular classification.

        Test PyTorchTabularClassifier fit() and get_results() methods for a
        classification problem using Adam optimizer.
        """
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        neural_network.fit(datasource)
        assert_results(model=neural_network)

    @unit_test
    def test_gradient_set_after_fitting(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests that the gradient var is set after fitting."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        neural_network.fit(datasource)
        assert hasattr(neural_network, "_training_epoch_end_gradients")

    @unit_test
    def test_specify_n_classes(
        self,
        datasource: DataFrameSource,
    ) -> None:
        """Tests specifying number of classes explicitly works.

        Tests the functionality where n_classes can be specified
        when initialising the classifier model. Required for running
        prediction, where the dataset doesn't contain a target.
        """
        datasource.load_data()
        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = DataStructure(table=TABLE_NAME)
        inference_network = PyTorchTabularClassifier(
            datastructure=inference_datastructure,
            schema=BitfountSchema(inference_datasource, table_name=TABLE_NAME),
            epochs=1,
            n_classes=5,
        )
        assert inference_network.n_classes == 5

    @unit_test
    def test_init_datastructure_no_target(
        self,
    ) -> None:
        """Tests DataStructure with no target.

        Test that a DataStructure can be initialised without specifying
        a target, as this is an optional argument now, and needs to be
        for unsupervised datasets.
        """
        inference_datastructure = DataStructure(table=TABLE_NAME)
        assert inference_datastructure.target is None

    @unit_test
    def test_set_number_of_classes(self, datasource: DataFrameSource) -> None:
        """Tests that n_classes override works."""
        datasource.load_data()
        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = DataStructure(table=TABLE_NAME)
        inference_datastructure.target = None
        inference_schema = BitfountSchema(inference_datasource, table_name=TABLE_NAME)
        inference_network = PyTorchTabularClassifier(
            datastructure=inference_datastructure,
            schema=inference_schema,
            epochs=1,
            n_classes=2,
        )
        table_schema = inference_schema.get_table_schema(TABLE_NAME)
        inference_network.set_number_of_classes(table_schema)

    @unit_test
    def test_no_classes_raises_error(self, datasource: DataFrameSource) -> None:
        """Ensures error raised if unknown number of classes.

        Tests that error is raised when both no target is specified in data,
        and no n_classes is explicitly defined.
        """
        datasource.load_data()
        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = DataStructure(table=TABLE_NAME)
        inference_network = PyTorchTabularClassifier(
            datastructure=inference_datastructure,
            schema=BitfountSchema(inference_datasource, table_name=TABLE_NAME),
            epochs=1,
        )
        with pytest.raises(ValueError):
            inference_network.initialise_model()

    @unit_test
    def test_prediction(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test that prediction works with trained model."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        model.fit(datasource)
        model.predict(datasource)

    @unit_test
    def test_prediction_empty_testset(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test that prediction fails if no test data is provided."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        model.fit(datasource)
        empty_datasource = DataFrameSource(
            datasource.data, data_splitter=PercentageSplitter(0, 0)
        )
        with pytest.raises(ValueError):
            model.predict(empty_datasource)

    @integration_test
    def test_prediction_after_train(
        self, datasource: DataFrameSource, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Tests Tabular classification.

        Test PyTorchTabularClassifier fit() and predict() methods for a
        classification problem.
        """
        datastructure = DataStructure(target="TARGET", table=TABLE_NAME)
        training_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
            batch_size=16,
        )
        training_network.fit(datasource)

        training_network.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)

        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = DataStructure(table=TABLE_NAME)
        inference_network = PyTorchTabularClassifier(
            datastructure=inference_datastructure,
            schema=BitfountSchema(inference_datasource, table_name=TABLE_NAME),
            epochs=1,
            n_classes=2,
        )
        inference_network.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert inference_network._initialised
        preds = inference_network.predict(inference_datasource)
        assert preds is not None

        mocker.patch.object(_BitfountDataset, "_set_column_name_attributes")
        mocker.patch.object(_BitfountDataset, "_reformat_data")

        db_dataset = _BitfountDataset(
            datasource=datasource,
            data_split=Mock(value="test"),
            schema=Mock(),
            selected_cols=Mock(),
            selected_cols_semantic_types=Mock(),
        )

        assert len(preds) == len(db_dataset.get_dataset_split(DataSplit.TEST))
        assert inference_network.n_classes == preds[0].shape[0]

    @unit_test
    def test_classification_with_continuous_data_only(
        self, datasource: DataFrameSource
    ) -> None:
        """Tests calling fit() with continuous only features."""
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["A", "B", "C", "D", "TARGET"],
            table=TABLE_NAME,
        )
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=1,
            optimizer=Optimizer("Adam"),
            batch_size=32,
        )
        neural_network.fit(datasource)

    @integration_test
    def test_fit_eval_with_continuous_data_only(
        self, datasource: DataFrameSource
    ) -> None:
        """Tests calling fit& eval with continuous only features."""
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["A", "B", "C", "D", "TARGET"],
            table=TABLE_NAME,
        )
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=1,
            optimizer=Optimizer("Adam"),
            batch_size=32,
        )
        neural_network.fit(datasource)
        assert_results(neural_network)

    @unit_test
    def test_classification_with_categorical_data_only(
        self, datasource: DataFrameSource
    ) -> None:
        """Tests calling fit() with categorical only features."""
        force_stype = {"categorical": ["E", "F", "G", "H"]}
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["E", "F", "G", "H", "M", "N", "O", "P", "TARGET"],
            table=TABLE_NAME,
        )
        datastructure._force_stype = cast(
            MutableMapping[_SemanticTypeValue, List[str]], force_stype
        )
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=1,
            optimizer=Optimizer("Adam"),
            batch_size=32,
        )
        neural_network.fit(datasource)

    @integration_test
    def test_classification_no_optimizer_params(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Confirms that optimizer works without params provided."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            optimizer=Optimizer("Adam"),
        )
        model.fit(datasource)

        model_optimizer: Optimizer = model.optimizer
        assert model_optimizer.name == "Adam"
        assert model_optimizer.params == {}

    @integration_test
    def test_classification_custom_scheduler(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Confirms that training works with a custom scheduler."""
        epochs = 2
        batch_size = 16
        datasource.load_data()
        table_schema = TableSchema(TABLE_NAME)
        table_schema.add_dataframe_features(datasource)
        # split data in DataBunch into training, validation, test sets
        _BitfountDataBunch(datastructure, table_schema, datasource)
        assert datasource._train_idxs is not None
        total_steps = int(len(datasource._train_idxs) * epochs / batch_size)
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=epochs,
            batch_size=batch_size,
            optimizer=Optimizer("Adam"),
            scheduler=Scheduler(
                "OneCycleLR", {"max_lr": 0.01, "total_steps": total_steps}
            ),
        )

        model.fit(datasource)

        model_scheduler = cast(Scheduler, model.scheduler)
        assert model_scheduler.name == "OneCycleLR"
        assert model_scheduler.params == {"max_lr": 0.01, "total_steps": total_steps}
        assert_results(model=model)

    @integration_test
    def test_classification_swa(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test classification with stochastic weight averaging."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            optimizer=Optimizer("Adam"),
            swa=True,
        )

        model.fit(datasource)
        assert_results(model=model)

    @integration_test
    def test_classification_lamb_optimizer(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests classification with a different optimizer."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            optimizer=Optimizer("Lamb", {"lr": 0.01}),
        )

        neural_network.fit(datasource)
        assert_results(model=neural_network)

    @unit_test
    def test_optimizer_not_supported(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests classification with a different optimizer."""
        with pytest.raises(ValueError):
            model = PyTorchTabularClassifier(
                datastructure=datastructure,
                schema=BitfountSchema(),
                epochs=1,
                batch_size=16,
                optimizer=Optimizer("FooBar", {"lr": 0.01}),
            )

            model.fit(datasource)

    @unit_test
    def test_tabnet_passed_to_tabular_classifier_raises_error(
        self, datastructure: DataStructure
    ) -> None:
        """Ensures error is raised if tabnet model passed to tabular classifier."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        with pytest.raises(ValueError):
            PyTorchTabularClassifier(
                model_structure=ms, datastructure=datastructure, epochs=2
            )

    @integration_test
    def test_multilabel_classification(self) -> None:
        """Tests multilabel classification works."""
        datastructure = create_datastructure(multilabel=True)
        datasource = create_datasource(classification=True, multilabel=True)
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            multilabel=True,
        )
        neural_network.fit(datasource)
        assert_results(model=neural_network)

    @unit_test
    def test_multilabel_has_correct_loss_funct(self) -> None:
        """Test that the correct loss function is loaded ."""
        datastructure = create_datastructure(multilabel=True)

        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            multilabel=True,
        )
        assert issubclass(neural_network.loss_func, nn.BCEWithLogitsLoss)  # type: ignore[arg-type] # reason: mypy gives incompatible type error "Optional[Callable[..., Any]]"; expected "type" # noqa: B950

    @integration_test
    def test_multilabel_multitask_classification(self) -> None:
        """Tests multilabel multitask classification works."""
        datastructure, datasource = get_datastructure_and_datasource(
            classification=True,
            multilabel=True,
            multihead=True,
            multihead_size=2,
            loss_weights=True,
        )
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
            multilabel=True,
        )
        neural_network.fit(datasource)
        assert_results(model=neural_network)

    @unit_test
    def test_serialization_deserialization_before_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Tests serialize() and deserialize() method before fitting."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
            batch_size=16,
        )
        neural_network.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)

        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=2,
        )
        model.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert model._initialised

    @unit_test
    def test_serialization_deserialization_after_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Tests serialize() and deserialize() methods after fitting."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )

        neural_network.fit(datasource)
        neural_network.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), epochs=2
        )
        neural_network.fit(datasource)
        neural_network.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        preds, targs = neural_network.evaluate(neural_network.test_dl)
        assert isinstance(preds, np.ndarray)
        assert isinstance(targs, np.ndarray)

    @unit_test
    def test_tabular_invalid_model_structure(
        self, datastructure: DataStructure
    ) -> None:
        """Tests error raised on invalid tabular model structure."""
        with pytest.raises(ValueError):
            PyTorchTabularClassifier(
                model_structure=NeuralNetworkPredefinedModel("resnet18"),
                datastructure=datastructure,
                epochs=1,
                batch_size=16,
            )

    @unit_test
    def test_image_invalid_model_structure(self, datastructure: DataStructure) -> None:
        """Tests error raised on invalid image model structure."""
        with pytest.raises(ValueError):
            PyTorchImageClassifier(
                model_structure=FeedForwardModelStructure(),
                datastructure=datastructure,
                epochs=1,
                batch_size=16,
            )

    @unit_test
    def test_tabular_classifier_split_dataloader_output(self) -> None:
        """Tests tabular classifier split dataloader output."""
        data = torch.stack((torch.ones(8), torch.ones(8), torch.ones(8)), dim=1)
        datasource = DataFrameSource(pd.DataFrame(data, columns=["A", "B", "TARGET"]))
        datastructure = DataStructure(target=["TARGET"], table=TABLE_NAME)
        datastructure._force_stype = {
            "categorical": ["TARGET", "A"],
            "continuous": ["B"],
        }
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=2,
        )
        # Need to call the below to initialize the dataloaders
        model.initialise_model(datasource)
        test_data = (
            torch.stack((torch.ones(8), torch.ones(8)), dim=1),
            torch.stack((torch.ones(8), torch.ones(8)), dim=1),
        )
        split_data = model._split_dataloader_output(test_data)
        assert len(split_data) == 3
        assert split_data[0][0].float().mean() == 1.0
        assert split_data[0][1].float().mean() == 1.0
        assert split_data[1].mean() == 1.0
        assert split_data[2] is None

    #
    @unit_test
    def test_image_classifier_split_dataloader_output_categories(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests image classifier dataloader splitting with categories."""
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_structure=NeuralNetworkPredefinedModel("resnet18"),
            epochs=2,
        )

        # Need to call the below to initialize the dataloaders
        model.initialise_model(datasource)

        data = (
            torch.ones(8),
            torch.stack((torch.ones(8), torch.zeros(8), torch.ones(8)), dim=1),
        )
        split_data = model._split_dataloader_output(data)
        assert len(split_data) == 3
        assert cast(torch.Tensor, split_data[0]).mean() == 1.0
        assert split_data[1].mean() == 1.0
        assert cast(torch.Tensor, split_data[2]).sum() == 8

    @unit_test
    def test_image_classifier_create_model_cnn_model_structure(self) -> None:
        """Tests image classifier creation with CNN structure."""
        data = create_dataset(image=True)
        ds = DataFrameSource(data)
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["image", "TARGET"],
            image_cols=["image"],
            table=TABLE_NAME,
        )
        model_structure = CNNModelStructure(pooling_function="avg")
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_structure=model_structure,
            epochs=2,
        )
        # Need to call the below to initialize the dataloaders
        model.initialise_model(ds)
        torch_model = model._create_model()
        assert isinstance(torch_model, torch.nn.Module)
        assert isinstance(
            cast(nn.ModuleList, torch_model.pooling_functions)[0], torch.nn.AvgPool2d
        )

    @unit_test
    def test_image_classifier_create_model_predefined_structure(self) -> None:
        """Tests image classifier creation with predefined structure."""
        data = create_dataset(image=True)
        ds = DataFrameSource(data, image_col=["image"])
        datastructure = DataStructure(
            target="TARGET", selected_cols=["image", "TARGET"], table=TABLE_NAME
        )
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_structure=NeuralNetworkPredefinedModel("resnet18"),
            epochs=2,
        )

        model.initialise_model(ds)
        torch_model = model._create_model()
        assert isinstance(torch_model, torch.nn.Module)
        assert cast(nn.Linear, torch_model.fc).out_features == 2

    @unit_test
    def test_image_classifier_multilabel_loss(self) -> None:
        """Tests image classifier with multilabel loss function."""
        datastructure = DataStructure(
            target="TARGET", selected_cols=["image", "TARGET"], table=TABLE_NAME
        )
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_structure=NeuralNetworkPredefinedModel("resnet18"),
            epochs=2,
            multilabel=True,
        )
        assert model.loss_func == torch.nn.BCEWithLogitsLoss

    @unit_test
    def test_image_classifier_loss_func_not_recognised(self) -> None:
        """Tests error raised if unknown loss_func supplied."""
        datastructure = DataStructure(
            target="TARGET", selected_cols=["image", "TARGET"], table=TABLE_NAME
        )
        with pytest.raises(ValueError):
            PyTorchImageClassifier(
                datastructure=datastructure,
                schema=BitfountSchema(),
                model_structure=NeuralNetworkPredefinedModel("resnet18"),
                custom_loss_func="test",
                epochs=2,
            )

    @integration_test
    def test_image_classifier_run_training(self) -> None:
        """Tests training of image classifier."""
        data = create_dataset(image=True)
        data = data[:500]
        ds = DataFrameSource(data)
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["image", "TARGET"],
            image_cols=["image"],
            table=TABLE_NAME,
        )
        model_structure = CNNModelStructure(
            layers=[16, 32], ff_layers=[500], ff_dropout_probs=[0.1]
        )
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=3,
            model_structure=model_structure,
            batch_size=64,
            optimizer=Optimizer("RAdam", {"lr": 0.01}),
        )
        model.fit(ds)
        assert_results(model=model)

    @integration_test
    def test_image_classifier_run_training_with_custom_transformations(self) -> None:
        """Tests training of image classifier."""
        data = create_dataset(image=True)
        data = data[:500]
        ds = DataFrameSource(data)
        datastructure = DataStructure(
            table=TABLE_NAME,
            target="TARGET",
            selected_cols=["image", "TARGET"],
            image_cols=["image"],
            batch_transforms=[
                {
                    "image": {
                        "step": "train",
                        "output": True,
                        "arg": "image",
                        "transformations": [
                            {"Resize": {"height": 224, "width": 224}},
                            "Normalize",
                            "HorizontalFlip",
                            "ToTensorV2",
                        ],
                    }
                },
                {
                    "image": {
                        "step": "validation",
                        "output": True,
                        "arg": "image",
                        "transformations": [
                            {"Resize": {"height": 224, "width": 224}},
                            "Normalize",
                            "ToTensorV2",
                        ],
                    }
                },
                {
                    "image": {
                        "step": "test",
                        "output": True,
                        "arg": "image",
                        "transformations": [
                            {"Resize": {"height": 224, "width": 224}},
                            "Normalize",
                            "ToTensorV2",
                        ],
                    }
                },
            ],
        )
        model_structure = CNNModelStructure(
            layers=[16, 32], ff_layers=[500], ff_dropout_probs=[0.1]
        )
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=3,
            model_structure=model_structure,
            batch_size=64,
            optimizer=Optimizer("RAdam", {"lr": 0.01}),
        )
        model.fit(ds)
        assert_results(model=model)

    @integration_test
    def test_image_classifier_fit_multiple_images(self) -> None:
        """Tests that the image classifier works with multiple images per row."""
        data = create_dataset(classification=True, multiimage=True, img_size=2)
        datasource = DataFrameSource(data[:64])
        datastructure = DataStructure(
            target="TARGET",
            selected_cols=["image1", "image2", "TARGET"],
            image_cols=["image1", "image2"],
            table=TABLE_NAME,
        )
        model = PyTorchImageClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
        )
        model.fit(datasource)

    @unit_test
    def test_classification_with_custom_metrics(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Tests calling fit() with different metrics."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            optimizer=Optimizer("Adam"),
            batch_size=32,
        )
        metric_results = neural_network.fit(
            datasource,
            metrics={
                "AUC": ClassificationMetric(
                    partial(roc_auc_score, multi_class="ovr", average="macro"), True
                )
            },
        )
        assert "AUC" in cast(Dict[str, str], metric_results).keys()
        assert "validation_loss" in cast(Dict[str, str], metric_results).keys()
        assert len(cast(Dict[str, str], metric_results)) == 2

    @unit_test
    def test_tensorboard_logger_default(self, datastructure: DataStructure) -> None:
        """Tests that the default lightning logger is TensorBoard."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )

        assert isinstance(model._pl_logger, TensorBoardLogger)

    @unit_test
    def test_csv_logger(
        self, datastructure: DataStructure, tmpdir: py.path.local
    ) -> None:
        """Tests that CSVLogger works."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=10,
            logger_config=LoggerConfig(
                name="CSVLogger", save_dir=cast(Path, tmpdir.strpath)
            ),
        )
        assert isinstance(model._pl_logger, CSVLogger)

    @unit_test
    def test_mlflow_logger(
        self, datastructure: DataStructure, tmpdir: py.path.local
    ) -> None:
        """Tests that MLFlowLogger works."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=10,
            logger_config=LoggerConfig(
                name="MLFlow", save_dir=cast(Path, tmpdir.strpath)
            ),
        )
        assert isinstance(model._pl_logger, MLFlowLogger)

    @unit_test
    def test_neptune_logger(self, datastructure: DataStructure) -> None:
        """Tests that NeptuneLogger works."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=10,
            logger_config=LoggerConfig(name="Neptune"),
        )
        assert isinstance(model._pl_logger, NeptuneLogger)

    @unit_test
    def test_testtube_logger(
        self, datastructure: DataStructure, tmpdir: py.path.local
    ) -> None:
        """Tests that TestTubeLogger works."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=10,
            logger_config=LoggerConfig(
                name="TestTube", save_dir=cast(Path, tmpdir.strpath)
            ),
        )
        assert isinstance(model._pl_logger, TestTubeLogger)

    @unit_test
    def test_wandb_logger(
        self, datastructure: DataStructure, tmpdir: py.path.local
    ) -> None:
        """Tests that WandbLogger works."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            steps=10,
            logger_config=LoggerConfig(
                name="WeightsAndBiases",
                save_dir=cast(Path, tmpdir.strpath),
                params={"offline": True},
            ),
        )
        assert isinstance(model._pl_logger, WandbLogger)

    @unit_test
    def test__fit_federated(
        self,
        datastructure: DataStructure,
        mock_bitfount_session: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Tests private _fit_federated method.

        Checks that DistributedModelMixIn._fit_federated helper method creates
        correct instances and runs the modeller correctly.
        """
        # Create model to test
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )

        # Patch out the modeller's run method as we only care how it is called
        # from _fit_federated.

        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")

        # Run method
        pod_identifiers = ["bitfount/adult", "bitfount/adult2"]
        model._fit_federated(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        # Check run method was called correctly
        # TODO: [BIT-983] Should this check that the Modeller was instantiated
        #       correctly? Related to whether we should mock out the helper calls.
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers, model_out=None
        )

    @unit_test
    @pytest.mark.parametrize("evaluate", [True, False], ids=["evaluate", "no_evaluate"])
    def test__fit_evaluate_federated_expands_datastructure_pod_identifiers(
        self,
        datastructure: DataStructure,
        evaluate: bool,
        mock_bitfount_session: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Tests private `_fit_federated` and `_evaluate_federated` methods.

        Checks that the method expands pod identifiers in the datastructure if they are
        not provided in full.
        """
        datastructure.table = {"pod1": "pod1_table", "pod2": "pod2_table"}

        # Create model to test
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )

        # Patch out the modeller's run method as we only care how it is called
        # from _fit_federated.
        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")

        # Run method
        pod_identifiers = ["bitfount/adult", "bitfount/adult2"]
        if evaluate:
            model._evaluate_federated(
                pod_identifiers=pod_identifiers,
                private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
            )
        else:
            model._fit_federated(
                pod_identifiers=pod_identifiers,
                private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
            )

        # Check run method was called correctly
        # TODO: [BIT-983] Should this check that the Modeller was instantiated
        #       correctly? Related to whether we should mock out the helper calls.
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers, model_out=None
        )

        # The username prepended is taken from the Mocked Bitfount Session
        assert model.datastructure.table == {
            "test_username/pod1": "pod1_table",
            "test_username/pod2": "pod2_table",
        }

    @unit_test
    def test_fit_method_with_federated_arguments(
        self, datastructure: DataStructure, mocker: MockerFixture
    ) -> None:
        """Test fit method with federated arguments detected correctly."""
        mock_fit_federated_method = mocker.patch(
            "bitfount.federated.mixins._DistributedModelMixIn._fit_federated",
        )
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        pod_identifiers = ["bitfount/adult", "bitfount/adult2"]
        private_key_or_file = TEST_SECURITY_FILES / "test_private.testkey"
        model.fit(
            pod_identifiers=pod_identifiers,
            private_key_or_file=private_key_or_file,
        )
        mock_fit_federated_method.assert_called_once_with(
            pod_identifiers=pod_identifiers, private_key_or_file=private_key_or_file
        )

    @unit_test
    def test_evaluate_method_with_remote_arguments(
        self, datastructure: DataStructure, mocker: MockerFixture
    ) -> None:
        """Test evaluate method with remote arguments detected correctly."""
        mock_evaluate_federated_method = mocker.patch(
            "bitfount.federated.mixins._DistributedModelMixIn._evaluate_federated",
        )
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        pod_identifiers = ["bitfount/adult", "bitfount/adult2"]
        private_key_or_file = TEST_SECURITY_FILES / "test_private.testkey"
        model.evaluate(
            pod_identifiers=pod_identifiers,
            private_key_or_file=private_key_or_file,
        )
        mock_evaluate_federated_method.assert_called_once_with(
            pod_identifiers=pod_identifiers, private_key_or_file=private_key_or_file
        )

    @unit_test
    def test__evaluate_federated(
        self,
        datastructure: DataStructure,
        mock_bitfount_session: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Tests private _evaluate_federated method.

        Checks that DistributedModelMixIn._evaluate_federated helper method creates
        correct instances and runs the modeller correctly.
        """
        # Create model to test
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )

        # Patch out the modeller's run method as we only care how it is called
        # from _fit_federated.

        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")

        # Run method
        pod_identifiers = ["bitfount/adult", "bitfount/adult2"]
        model._evaluate_federated(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        # Check run method was called correctly
        # TODO: [BIT-983] Should this check that the Modeller was instantiated
        #       correctly? Related to whether we should mock out the helper calls.
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers, model_out=None
        )

    @unit_test
    def test_set_pod_identifier(self, datastructure: DataStructure) -> None:
        """Tests `set_pod_identifier` method."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
        )
        model.set_pod_identifier("test_pod")
        assert model.pod_identifier == "test_pod"

    @integration_test
    def test_training_with_iterable_dataloader(
        self, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Tests training with an iterable dataloader."""
        db_conn = DatabaseConnection(db_session)
        datasource = DatabaseSource(db_conn)
        schema = BitfountSchema(
            datasource,
            force_stypes={"dummy_data": {"categorical": ["TARGET"]}},
            table_name="dummy_data",
        )
        data_structure = DataStructure(target="TARGET", table="dummy_data")

        model = PyTorchTabularClassifier(
            datastructure=data_structure,
            schema=schema,
            epochs=1,
            batch_size=32,
        )
        model.fit(datasource)


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for PyTorch models."""

    def test_pytorch_classifier_serialization(
        self, datastructure: DataStructure
    ) -> None:
        """Tests tabular classifier serialization."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=2,
        )
        serialized_model = bf_dump(model)

        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model

        assert_vars_equal(vars(model), vars(deserialized_model))
        del deserialized_model

    def test_pytorch_classifier_serialization_w_scheduler(
        self, datastructure: DataStructure
    ) -> None:
        """Tests tabular classifier serialization."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=2,
            scheduler=Scheduler("OneCycleLR", {"max_lr": 0.01, "total_steps": 3}),
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model

        assert_vars_equal(vars(model), vars(deserialized_model))
        del deserialized_model

    def test_image_classifier_serialization(self, datastructure: DataStructure) -> None:
        """Test PyTorchImageClassifier serialization."""
        model = PyTorchImageClassifier(
            model_structure=NeuralNetworkPredefinedModel("resnet18"),
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model

        assert_vars_equal(vars(model), vars(deserialized_model))

    def test_image_classifier_serialization_cnn(
        self, datastructure: DataStructure
    ) -> None:
        """Test PyTorchImageClassifier serialization."""
        model = PyTorchImageClassifier(
            model_structure=CNNModelStructure(pooling_function="avg"),
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
            batch_size=16,
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model

        assert_vars_equal(vars(model), vars(deserialized_model))

    def test_tabnet_serialization(self, datastructure: DataStructure) -> None:
        """Test TabNet serialization."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            balance_class_weights=True,
            epochs=2,
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model

        assert_vars_equal(vars(model), vars(deserialized_model))
        del deserialized_model

    def test_logreg_serialization_and_deserialization(
        self, datastructure: DataStructure
    ) -> None:
        """Tests serialization and deserialization."""
        model = PyTorchLogisticRegressionClassifier(
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
        )
        serialized_model = bf_dump(model)

        # Check attributes in dumped schema
        for attr in (
            "bias",
            "l1_regularization_weight",
            "l2_regularization_weight",
            "embed_categorical",
            "embed_categorical_dropout",
        ):
            assert attr in serialized_model

        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        del serialized_model
        # Check attributes match between original and reloaded
        for attr in (
            "bias",
            "l1_regularization_weight",
            "l2_regularization_weight",
            "embed_categorical",
            "embed_categorical_dropout",
        ):
            assert getattr(model, attr) == getattr(deserialized_model, attr)
        del deserialized_model


@backend_test
@unit_test
class TestPyTorchLogisticRegressionClassifier:
    """Tests for PyTorchLogisticRegressionClassifier."""

    @fixture
    def logistic_regression_classifier(
        self, datastructure: DataStructure, schema: BitfountSchema
    ) -> PyTorchLogisticRegressionClassifier:
        """Logistic regression classifier to test against."""
        return PyTorchLogisticRegressionClassifier(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
        )

    def test_init_removes_model_structure(
        self,
        caplog: LogCaptureFixture,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests init overrides a provided model_structure."""
        empty_model_structure = FeedForwardModelStructure(
            layers=[], dropout_probs=[], mish_activation_function=False
        )

        log_reg = PyTorchLogisticRegressionClassifier(
            model_structure=Mock(spec=FeedForwardModelStructure),
            datastructure=datastructure,
            schema=schema,
            epochs=1,
        )

        # Check logs
        warning_logs = get_warning_logs(caplog)
        assert (
            "Specified model structure is not compatible with "
            "PyTorchLogisticRegressionClassifier; will be overridden." in warning_logs
        )

        # Check model_structure is as expected
        assert log_reg.model_structure == empty_model_structure

    def test_multilabel_not_allowed(
        self,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests init raises error if multilabel requested."""
        with pytest.raises(
            ValueError,
            match=re.escape(
                "PyTorchLogisticRegressionClassifier does not support multilabel "
                "classification problems."
            ),
        ):
            PyTorchLogisticRegressionClassifier(
                datastructure=datastructure,
                schema=schema,
                epochs=1,
                multilabel=True,
            )

    def test_multihead_not_allowed(
        self,
        caplog: LogCaptureFixture,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests init overrides if multihead requested."""
        datastructure.multihead_size = 3

        log_reg = PyTorchLogisticRegressionClassifier(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
        )

        # Check warning logs
        warning_logs = get_warning_logs(caplog)
        assert "Multihead LogReg is not supported, setting to 1." in warning_logs
        # Check final attribute value
        assert cast(NeuralNetworkModelStructure, log_reg.model_structure).num_heads == 1

    def test_init_sets_cross_entropy_loss(
        self,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests cross entropy loss set as default."""
        log_reg = PyTorchLogisticRegressionClassifier(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
        )
        assert log_reg.loss_func == CrossEntropyLoss

    def test_init_only_allows_cross_entropy_loss(
        self,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests init throws error if non-CE loss."""
        with pytest.raises(
            ValueError, match=re.escape("This loss function is not currently supported")
        ):
            PyTorchLogisticRegressionClassifier(
                datastructure=datastructure,
                schema=schema,
                epochs=1,
                custom_loss_func=Mock(),
            )

    @pytest.mark.parametrize(
        argnames="embed_categorical",
        argvalues=(
            pytest.param(True, id="embed categorical"),
            pytest.param(False, id="don't embed categorical"),
        ),
    )
    def test__create_model(
        self,
        caplog: LogCaptureFixture,
        datastructure: DataStructure,
        embed_categorical: bool,
        logistic_regression_classifier: PyTorchLogisticRegressionClassifier,
        mocker: MockerFixture,
        schema: BitfountSchema,
    ) -> None:
        """Tests _create_model with multiple categorical settings."""
        # Set embed strategy
        logistic_regression_classifier.embed_categorical = embed_categorical

        # Extract details about data
        ignore_cols_for_training = datastructure.get_columns_ignored_for_training()
        table_schema = schema.get_table_schema(datastructure.get_table_name())
        num_categorical = table_schema.get_num_categorical(
            ignore_cols=ignore_cols_for_training
        )
        num_continuous = table_schema.get_num_continuous(
            ignore_cols=ignore_cols_for_training
        )

        # Mock out calls to make assertions easier
        mock_calculate_embeddings = mocker.patch(
            "bitfount.backends.pytorch.models.models._calculate_embedding_sizes",
            return_value=[(i, i + 1) for i in range(5)],
            autospec=True,
        )
        mock_underlying_model_constructor = mocker.patch(
            "bitfount.backends.pytorch.models.models._PyTorchLogisticRegression",
            autospec=True,
        )

        with caplog.at_level(logging.INFO):
            model = logistic_regression_classifier._create_model()

        assert model is mock_underlying_model_constructor.return_value

        # Way constructor is called depends on embed strategy
        info_logs = get_info_logs(caplog)
        if embed_categorical:
            mock_underlying_model_constructor.assert_called_once_with(
                num_classes=logistic_regression_classifier.n_classes,
                num_continuous=num_continuous,
                embedding_sizes=mock_calculate_embeddings.return_value,
                embedding_dropout_frac=logistic_regression_classifier.embed_categorical_dropout,  # noqa: B950
                bias=logistic_regression_classifier.bias,
            )
            assert (
                "Generating Categorical Embeddings for categorical features."
                in info_logs
            )
        else:
            mock_underlying_model_constructor.assert_called_once_with(
                num_classes=logistic_regression_classifier.n_classes,
                input_dim=num_continuous + num_categorical,
                bias=logistic_regression_classifier.bias,
            )
            assert (
                "No categorical embedding requested; categorical data should be "
                "label-encoded." in info_logs
            )

    @pytest.mark.parametrize(
        argnames="embed_categorical",
        argvalues=(
            pytest.param(True, id="embed categorical"),
            pytest.param(False, id="don't embed categorical"),
        ),
    )
    def test__split_dataloader_output(
        self,
        datastructure: DataStructure,
        embed_categorical: bool,
        logistic_regression_classifier: PyTorchLogisticRegressionClassifier,
        schema: BitfountSchema,
    ) -> None:
        """Tests _split_dataloader_output for multiple categorical settings."""
        batch_size = 32

        # Set embed strategy
        logistic_regression_classifier.embed_categorical = embed_categorical

        # Get data needed to construct tensors
        ignore_cols_for_training = datastructure.get_columns_ignored_for_training()
        table_schema = schema.get_table_schema(datastructure.get_table_name())
        num_categorical = table_schema.get_num_categorical(
            ignore_cols=ignore_cols_for_training
        )
        num_continuous = table_schema.get_num_continuous(
            ignore_cols=ignore_cols_for_training
        )

        # Create data tensor
        cont_data_tensor = torch.rand(batch_size, num_continuous)
        cat_data_tensor = torch.randint(10, (batch_size, num_categorical))
        data_tensor = torch.hstack([cat_data_tensor, cont_data_tensor])

        # Create supplementary tensor
        sup_tensor = torch.rand(batch_size, 1)  # "weights"

        (
            (output_cat_tensor, output_cont_tensor),
            weights,
            categories,
        ) = logistic_regression_classifier._split_dataloader_output(
            (data_tensor, sup_tensor)
        )

        # Expected outputs differ depending on settings
        if embed_categorical:
            # Categorical data tensor will be transposed
            assert output_cat_tensor.size() == (num_categorical, batch_size)
        else:
            # Otherwise will be normal
            assert output_cat_tensor.size() == (batch_size, num_categorical)
        # Should be long()
        assert not torch.is_floating_point(output_cat_tensor)

        assert output_cont_tensor.size() == (batch_size, num_continuous)
        assert torch.is_floating_point(output_cont_tensor)

        assert weights.size() == (batch_size,)
        assert torch.is_floating_point(weights)

        assert categories is None

    @pytest.mark.parametrize(
        argnames="l1_weight",
        argvalues=(
            pytest.param(0.5, id="l1 regularisation"),
            pytest.param(None),
        ),
    )
    @pytest.mark.parametrize(
        argnames="l2_weight",
        argvalues=(
            pytest.param(0.5, id="l2 regularisation"),
            pytest.param(None),
        ),
    )
    def test__get_loss(
        self,
        l1_weight: Optional[float],
        l2_weight: Optional[float],
        logistic_regression_classifier: PyTorchLogisticRegressionClassifier,
        mocker: MockerFixture,
    ) -> None:
        """Test _get_loss applies regularisation terms."""
        # Set regularisation parameters on model
        logistic_regression_classifier.l1_regularization_weight = l1_weight
        logistic_regression_classifier.l2_regularization_weight = l2_weight

        # Mock out super()._get_loss()
        super_loss_value = 10.0
        mock_super_loss = torch.tensor(super_loss_value)
        mocker.patch.object(
            BasePyTorchModel, "_get_loss", autospec=True, return_value=mock_super_loss
        )

        # Mock out linear layer weights
        mock_model_weights = torch.rand(64, 1)
        mock_model = mocker.patch.object(logistic_regression_classifier, "_model")
        mock_model.linear.weight = mock_model_weights

        # Create arbitrary sample weights
        sample_weightings = torch.rand(32, 1)
        sample_weightings_sum = sample_weightings.squeeze().sum()

        loss = logistic_regression_classifier._get_loss(
            output=Mock(), target=Mock(), loss_modifiers=(sample_weightings,)
        )

        # Value will differ depending on settings
        expected_loss = torch.tensor(super_loss_value)
        if l1_weight:
            expected_loss += l1_weight * (
                mock_model_weights.abs().sum() / sample_weightings_sum
            )
        if l2_weight:
            expected_loss += l2_weight * (
                mock_model_weights.pow(2).sum() / sample_weightings_sum
            )
        assert loss == expected_loss


@backend_test
class TestTabNetClassifier:
    """Tests for TabNetClassifier."""

    @integration_test
    def test_training_default_optimizer(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test training with default optimizer."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=6,
            patience=4,
            batch_size=64,
            virtual_batch_size=16,
            seed=43,
        )
        model.fit(datasource)
        preds, targs = model.evaluate()
        assert isinstance(preds, np.ndarray)
        assert isinstance(targs, np.ndarray)
        metrics = MetricCollection.create_from_model(model)
        results = metrics.compute(targs, preds)
        assert isinstance(results, dict)
        assert len(metrics.metrics) == len(BINARY_CLASSIFICATION_METRICS)
        assert results["AUC"] > AUC_THRESHOLD

    @unit_test
    def test_virtual_batch_size_higher_than_batch_size_raises_value_error(
        self, datastructure: DataStructure
    ) -> None:
        """Test virtual batch size higher than batch size raises value error."""
        ms = NeuralNetworkPredefinedModel("TabNet")

        with pytest.raises(ValueError):
            TabNetClassifier(
                model_structure=ms,
                datastructure=datastructure,
                schema=BitfountSchema(),
                epochs=5,
                batch_size=32,
                virtual_batch_size=64,
            )

    @integration_test
    def test_tabnet_init_db_query(
        self, datastructure: DataStructure, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Tests that model is initialised with a query datastructure."""
        db_datasource = DatabaseSource(
            DatabaseConnection(db_session, table_names=["dummy_data"])
        )
        schema = BitfountSchema(db_datasource, table_name="dummy_data")
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=schema,
            epochs=3,
            batch_size=64,
            virtual_batch_size=16,
            optimizer=Optimizer("AdaBelief", {"lr": 0.01}),
            seed=43,
        )
        model.initialise_model(db_datasource)
        assert model._databunch is not None
        assert model.n_classes == 2

    @unit_test
    def test_pod_id_set_for_modeller(
        self, datasource: DataFrameSource, mocker: MockerFixture, schema: BitfountSchema
    ) -> None:
        """Tests that pod_identifier is set for the modeller."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        datastructure = DataStructure(table={"pod_id": "test_table"}, target="TARGET")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=schema,
            epochs=3,
            batch_size=64,
            virtual_batch_size=16,
            optimizer=Optimizer("AdaBelief", {"lr": 0.01}),
            seed=43,
        )
        mock_table_schema = mocker.patch.object(
            BitfountSchema,
            "get_table_schema",
            return_value=schema.get_table_schema("test_table"),
        )
        model.train_dl = Mock(autospec=True)
        model.train_dl.get_y_dataframe.return_value = create_dataset(
            classification=True
        )
        mocker.patch.object(TabNetClassifier, "_create_model")
        mocker.patch.object(TabNetClassifier, "fit")
        model.initialise_model(context=ModelContext.MODELLER, data=datasource)
        assert model.pod_identifier == "pod_id"
        mock_table_schema.assert_called_once()

    @unit_test
    def test_virtual_batch_same_as_batch_size_is_accepted(
        self, datastructure: DataStructure
    ) -> None:
        """Test virtual batch size same as batch size accepted."""
        ms = NeuralNetworkPredefinedModel("TabNet")

        TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=5,
            batch_size=32,
            virtual_batch_size=32,
        )

    # TODO: [BIT-507] This test is intermittently failing on GHA
    @integration_test
    @pytest.mark.skip()
    def test_training_adabelief_optimizer(
        self, datasource: DataFrameSource, datastructure: DataStructure
    ) -> None:
        """Test training defaults."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=3,
            batch_size=64,
            virtual_batch_size=16,
            optimizer=Optimizer("AdaBelief", {"lr": 0.01}),
            seed=43,
        )
        model.fit(datasource, metrics={"auc": roc_auc_score})
        preds, targs = model.evaluate()
        assert isinstance(preds, np.ndarray)
        assert isinstance(targs, np.ndarray)
        metrics = MetricCollection.create_from_model(model)
        results = metrics.compute(targs, preds)
        assert isinstance(results, dict)
        assert len(metrics.metrics) == len(BINARY_CLASSIFICATION_METRICS)
        assert results["AUC"] > AUC_THRESHOLD

    @unit_test
    def test_serialization_before_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Test untrained model cannot be serialized.

        TODO: [BIT-1152] change this test once serialization/deserialization of unfitted
        model if fixed.
        """
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        # TODO: [BIT-1152] change this assertion
        assert not os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)

    @unit_test
    def test_deserialization_before_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Test untrained model cannot be deserialized.

        TODO: [BIT-1152] change this test once serialization/deserialization of unfitted
        model if fixed.
        """
        ms = NeuralNetworkPredefinedModel("TabNet")

        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
        )
        model.fit(datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)

        model2 = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model2.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        # TODO: [BIT-1152] change this assertion
        assert not model2._initialised

    @unit_test
    def test_serialization_deserialization_after_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Test trained model works after being serialized and deserialized."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=1,
        )
        model.fit(datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=2,
        )
        model.fit(datasource)
        model.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        model.evaluate()

    @unit_test
    def test_model_structure_not_provided(self, datastructure: DataStructure) -> None:
        """Test model structure not provided raises TypeError."""
        with pytest.raises(TypeError):
            TabNetClassifier(datastructure=datastructure, epochs=2)

    @unit_test
    def test_steps_not_accepted(self, datastructure: DataStructure) -> None:
        """Test steps not accepted for iterations."""
        ms = NeuralNetworkPredefinedModel("TabNet")
        with pytest.raises(ValueError):
            TabNetClassifier(
                datastructure=datastructure,
                schema=BitfountSchema(),
                model_structure=ms,
                steps=2,
            )

    @unit_test
    def test_incorrect_model_structure_provided(
        self, datastructure: DataStructure
    ) -> None:
        """Test incorrect model structure provided raises ValueError."""
        ms = NeuralNetworkPredefinedModel("NotTabNetModel")
        with pytest.raises(ValueError):
            TabNetClassifier(
                model_structure=ms,
                datastructure=datastructure,
                schema=BitfountSchema(),
                epochs=2,
            )

    @integration_test
    def test_multiclass_classification(self) -> None:
        """Test Multiclass classification."""
        dataset = create_dataset()
        dataset.TARGET = np.where(
            (dataset.TARGET == 0) & (dataset.C > 800), 2, dataset.TARGET
        )
        datasource = DataFrameSource(dataset)
        datastructure = DataStructure(target="TARGET", table=TABLE_NAME)
        ms = NeuralNetworkPredefinedModel("TabNet")
        model = TabNetClassifier(
            model_structure=ms,
            datastructure=datastructure,
            schema=BitfountSchema(),
            epochs=2,
            batch_size=16,
            virtual_batch_size=4,
            optimizer=Optimizer("RAdam"),
        )
        model.fit(datasource)
        preds, targs = model.evaluate()
        assert isinstance(preds, np.ndarray)
        assert isinstance(targs, np.ndarray)
        metrics = MetricCollection.create_from_model(model)
        results = metrics.compute(targs, preds)
        assert isinstance(results, dict)
        assert len(metrics.metrics) == len(MULTICLASS_CLASSIFICATION_METRICS)


@backend_test
@unit_test
class TestDifferentialPrivacy:
    """Tests related to differential privacy in PyTorch models."""

    @fixture
    def schema(self, datasource: DataFrameSource) -> BitfountSchema:
        """Fixture for schema."""
        return BitfountSchema(
            datasource,
            table_name=TABLE_NAME,
            force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
        )

    class DPTestModel(PyTorchTabularClassifier):
        """A custom classifier to make DP testing easier."""

        n_classes: int = 1

        def _create_model(self) -> nn.Module:  # type: ignore[override] # reason: incompatible return types # noqa: B950
            class Model(nn.Module):
                """A simplistic model for DP tests.

                Ensures DP compatible layers.
                """

                def __init__(self, input_size: int, output_size: int):
                    super().__init__()
                    self.linear = Linear(input_size, 10)
                    self.relu = ReLU()
                    self.output = Linear(10, output_size)

                def forward(self, x: Any) -> Any:
                    """Forward pass of the model."""
                    _x_cat, x_cont = x
                    fwd = self.linear(x_cont)
                    fwd = self.relu(fwd)
                    fwd = self.output(fwd)
                    return fwd

            ignore_cols = self.datastructure.ignore_cols[:]
            ignore_cols = _add_this_to_list(self.datastructure.target, ignore_cols)
            ignore_cols = _add_this_to_list(
                self.datastructure.loss_weights_col, ignore_cols
            )
            ignore_cols = _add_this_to_list(
                self.datastructure.ignore_classes_col, ignore_cols
            )
            num_continuous = len(
                [
                    i
                    for i in self.schema.get_feature_names(
                        TABLE_NAME, SemanticType.CONTINUOUS
                    )
                    if i not in ignore_cols
                ]
            )
            return Model(input_size=num_continuous, output_size=10)

    @fixture
    def dp_modeller_config(self) -> DPModellerConfig:
        """Modeller config for differential privacy."""
        return DPModellerConfig(max_epsilon=10.0)

    @fixture
    def dp_model(
        self,
        datastructure: DataStructure,
        dp_modeller_config: DPModellerConfig,
        schema: BitfountSchema,
    ) -> TestDifferentialPrivacy.DPTestModel:
        """Test model that implements DP."""
        return TestDifferentialPrivacy.DPTestModel(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
            batch_size=32,
            dp_config=dp_modeller_config,
        )

    def test__initialise_differential_privacy_autofixes_models(
        self,
        caplog: LogCaptureFixture,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        dp_modeller_config: DPModellerConfig,
        mocker: MockerFixture,
    ) -> None:
        """Tests autofixing of model modules works."""
        caplog.set_level(logging.DEBUG)
        # Ensure autofix is True
        dp_modeller_config.auto_fix = True

        mock_validate = mocker.patch.object(
            ModuleValidator,
            "validate",
            return_value=[UnsupportedModuleError("something isn't supported")],
            autospec=True,
        )
        mock_fix_and_validate = mocker.patch.object(
            ModuleValidator, "fix_and_validate", autospec=True
        )

        # Mock out wrapping model in Opacus privacy module
        mock_grad_sample_cls = mocker.patch(
            "bitfount.backends.pytorch.models.base_models.GradSampleModule",
            autospec=True,
        )

        # Create mock model
        mock_model = mocker.patch.object(dp_model, "_model", autospec=True)

        # Patch out train_dl updating
        mock_dl = create_autospec(_PyTorchBitfountDataLoader, instance=True)
        mock_dl.__len__.return_value = 1000
        dp_model.train_dl = mock_dl

        dp_model._initialise_differential_privacy()

        # Check strict validation was called
        mock_validate.assert_called_once_with(mock_model)
        # Check logger noted changes
        warning_logs = get_warning_logs(caplog)
        expected_warning = (
            "Some of the modules used in the model are incompatible "
            "with `opacus`, attempting to autofix."
        )
        assert expected_warning in warning_logs
        debug_logs = get_debug_logs(caplog)
        assert "Incompatible modules detected in model:" in debug_logs

        # Check model updated and fixed
        mock_grad_sample_cls.assert_called_once_with(
            mock_fix_and_validate.return_value,
            batch_first=True,
            loss_reduction=dp_modeller_config.loss_reduction,
        )
        assert dp_model._model is mock_grad_sample_cls.return_value

    def test__initialise_differential_privacy_raises_error_if_cannot_autofix_model(
        self,
        caplog: LogCaptureFixture,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        dp_modeller_config: DPModellerConfig,
        mocker: MockerFixture,
    ) -> None:
        """Tests error raised if unable to autofix model."""
        caplog.set_level(logging.DEBUG)
        # Ensure autofix is True
        dp_modeller_config.auto_fix = True

        mock_validate = mocker.patch.object(
            ModuleValidator,
            "validate",
            return_value=[UnsupportedModuleError("something isn't supported")],
            autospec=True,
        )
        mocker.patch.object(
            ModuleValidator,
            "fix_and_validate",
            side_effect=UnsupportedModuleError("fix and validate"),
            autospec=True,
        )

        mock_model = mocker.patch.object(dp_model, "_model", autospec=True)

        with pytest.raises(UnsupportedModuleError, match="fix and validate"):
            dp_model._initialise_differential_privacy()

        # Check strict validation was called
        mock_validate.assert_called_once_with(mock_model)
        # Check logger noted changes
        warning_logs = get_warning_logs(caplog)
        expected_warning = (
            "Some of the modules used in the model are incompatible "
            "with `opacus`, attempting to autofix."
        )
        assert expected_warning in warning_logs
        debug_logs = get_debug_logs(caplog)
        assert "Incompatible modules detected in model:" in debug_logs

    def test__initialise_differential_privacy_raises_error_if_incompatible_no_autofix(
        self,
        caplog: LogCaptureFixture,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        dp_modeller_config: DPModellerConfig,
        mocker: MockerFixture,
    ) -> None:
        """Tests error raised if model not validated and autofix not enabled."""
        caplog.set_level(logging.DEBUG)
        # Ensure autofix is False
        dp_modeller_config.auto_fix = False

        mock_validate = mocker.patch.object(
            ModuleValidator,
            "validate",
            side_effect=UnsupportedModuleError("custom error"),
            autospec=True,
        )
        mock_model = mocker.patch.object(dp_model, "_model", autospec=True)

        with pytest.raises(UnsupportedModuleError, match="custom error"):
            dp_model._initialise_differential_privacy()

        # Check strict validation was called
        mock_validate.assert_called_once_with(mock_model)
        # Check logger didn't note changes
        warning_logs = get_warning_logs(caplog)
        expected_warning = (
            "Some of the modules used in the model are incompatible "
            "with `opacus`, attempting to autofix."
        )
        assert expected_warning not in warning_logs
        debug_logs = get_debug_logs(caplog)
        assert "Incompatible modules detected in model:" not in debug_logs

    def test_differential_privacy_output(
        self,
        datasource: DataFrameSource,
        dp_model: TestDifferentialPrivacy.DPTestModel,
    ) -> None:
        """Tests custom tabular classifier differential privacy."""
        results = cast(Dict[str, str], dp_model.fit(datasource))

        assert "epsilon" in results
        assert "alpha" in results

    def test_differential_privacy_exceeded(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        mocker: MockerFixture,
        schema: BitfountSchema,
    ) -> None:
        """Tests that further training steps are not run when DP exceeded."""
        neural_network = TestDifferentialPrivacy.DPTestModel(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
            batch_size=32,
            dp_config=DPModellerConfig(max_epsilon=1.0),
        )

        # Patch out privacy spent calculator
        mocker.patch.object(
            PrivacyEngine, "get_epsilon", autospec=True, return_value=1.1
        )

        # Ensure training_step() isn't called when max_epsilon is exceeded
        ts = mocker.patch.object(neural_network, "training_step", autospec=True)
        neural_network.fit(datasource)
        ts.assert_not_called()

    def test_differential_privacy_config_serialization(
        self,
        datastructure: DataStructure,
        dp_modeller_config: DPModellerConfig,
        schema: BitfountSchema,
    ) -> None:
        """Tests the DP-specific serialization aspects."""
        neural_network = PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            epochs=1,
            batch_size=32,
            dp_config=dp_modeller_config,
        )

        # Serialization
        dumped = bf_dump(neural_network)
        assert "dp_config" in dumped
        # Deserialization
        loaded = bf_load(dumped, MAIN_MODEL_REGISTRY)
        assert loaded._dp_config == neural_network._dp_config

    def test__privacy_guarantees_exceeded_raises_exception_if_dp_engine_but_no_config(
        self,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        mocker: MockerFixture,
    ) -> None:
        """Tests _privacy_guarantees_exceeded errors if dp_engine but no config."""
        # Add engine
        mocker.patch.object(dp_model, "_dp_engine", autospec=True)
        # Ensure config is None
        dp_model._dp_config = None

        with pytest.raises(
            ValueError, match="DP Engine created but no configuration could be found."
        ):
            dp_model._privacy_guarantees_exceeded()

    def test_configure_optimizers_raises_exception_if_dp_engine_but_no_config(
        self,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        mocker: MockerFixture,
    ) -> None:
        """Tests _privacy_guarantees_exceeded errors if dp_engine but no config."""
        # Add engine
        mocker.patch.object(dp_model, "_dp_engine", autospec=True)
        # Ensure "model" created
        mocker.patch.object(dp_model, "_model", autospec=True)
        # Patch opt_func
        mocker.patch.object(dp_model, "_opt_func", new=Mock())
        # Ensure config is None
        dp_model._dp_config = None

        with pytest.raises(
            ValueError, match="DP Engine created but no configuration could be found."
        ):
            dp_model.configure_optimizers()

    def test__fit_local_raises_exception_if_dp_engine_but_no_config(
        self,
        datasource: DataFrameSource,
        dp_model: TestDifferentialPrivacy.DPTestModel,
        mocker: MockerFixture,
    ) -> None:
        """Tests _privacy_guarantees_exceeded errors if dp_engine but no config."""
        # Mock out lightning trainer
        # `autospec` set to True causes a RunTime error due to dynamic properties on the
        # trainer.
        mock_trainer = mocker.patch.object(dp_model, "_pl_trainer")

        def _unset_config(*_args: Any, **_kwargs: Any) -> None:
            dp_model._dp_config = None

        # Make sure that dp_config becomes "unset" somehow
        mock_trainer.fit.side_effect = _unset_config

        with pytest.raises(
            ValueError, match="DP Engine created but no configuration could be found."
        ):
            dp_model._fit_local(datasource)
