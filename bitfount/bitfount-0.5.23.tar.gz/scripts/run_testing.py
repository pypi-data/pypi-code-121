#!/usr/bin/env python
"""Evaluate a pretrained local model on local data."""
import logging
from typing import cast

import fire
import numpy as np
import pandas as pd
import yaml

from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.federated.utils import _MODELS
from bitfount.metrics import MetricCollection
from bitfount.runners.utils import setup_loggers
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
)
from bitfount.transformations.processor import TransformationProcessor

loggers = setup_loggers([logging.getLogger("bitfount")])


def evaluate_model(
    path_to_config_yaml: str, path_to_test_csv: str, path_to_model: str
) -> None:
    """Evaluates a model's performance."""
    with open(path_to_config_yaml) as f:
        config = yaml.safe_load(f)
    algorithm = config.pop("algorithm")
    schema_filename = config.pop("schema")
    batch_size = config.get("batch_size")
    datasource_args = config["datasource_args"]
    target = config["target"]

    # Load dataset
    data = pd.read_csv(path_to_test_csv)
    schema = BitfountSchema.load_from_file(schema_filename)
    if len(schema.tables) > 1:
        raise ValueError("Only single-table schemas are supported.")

    datasource = DataFrameSource(data=data, **datasource_args)
    # Transform dataset
    clean_data = CleanDataTransformation()
    normalize = NormalizeDataTransformation()
    processor = TransformationProcessor([clean_data, normalize], schema.tables[0])
    datasource.data = processor.transform(datasource.data)

    # Create datastructure and get test dataloader
    data_structure = DataStructure(target=target, table=schema.table_names[0])
    # TODO: [BIT-1167] process transformations here

    # Load model
    neural_network = _MODELS[algorithm](datastructure=data_structure, schema=schema)
    neural_network.initialise_model(data=datasource)
    test_data_loader = neural_network._databunch.get_train_dataloader(
        batch_size=batch_size
    )

    neural_network.deserialize(path_to_model)

    # Evaluate model on test dataloader
    preds, targs = neural_network.evaluate(test_data_loader)
    # TODO: [BIT-1604] Remove these cast statements once they become superfluous.
    preds = cast(np.ndarray, preds)
    targs = cast(np.ndarray, targs)
    metrics = MetricCollection.create_from_model(neural_network)
    results = metrics.compute(targs, preds)
    logging.info(str(results))


def main() -> None:
    """Script entry point."""
    fire.Fire(evaluate_model)


if __name__ == "__main__":
    main()
