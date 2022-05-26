# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""

import importlib
import logging
import os
from typing import Any, Dict, Optional

import numpy as np
from transformers import AutoTokenizer

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common._utils import (
    _get_language_code,
    create_unique_dir,
    is_data_labeling_run,
    prepare_run_properties,
    prepare_post_run_properties,
    save_script,
    save_conda_yml,
    scrub_system_exception,
    is_main_process,
    save_deploy_script
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, ScoringLiterals
from azureml.automl.dnn.nlp.ner._utils import log_metrics
from azureml.automl.dnn.nlp.ner.io.read.dataloader import load_and_validate_dataset
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer
from azureml.automl.runtime import data_transformation
from azureml.core.run import Run
from azureml.train.automl.runtime._entrypoints.utils.common import initialize_log_server

_logger = logging.getLogger(__name__)

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


def run(
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        **kwargs: Any
):
    """Invoke training by passing settings and write the output model.

    :param automl_settings: dictionary with automl settings
    :param mltable_data_json: mltable data json containing location of data
    """
    # Get Run Info
    current_run = Run.get_context()

    try:
        workspace = current_run.experiment.workspace

        # Parse settings
        automl_settings_obj = initialize_log_server(current_run, automl_settings)
        # checking if run is from data labeling project; data labeling run has different input dataset format
        is_labeling_run = is_data_labeling_run(current_run)
        # Get primary metric
        primary_metric = automl_settings_obj.primary_metric
        # Get model based on dataset language
        dataset_language = _get_language_code(automl_settings_obj.featurization)
        model_name, download_dir = get_model_from_language(dataset_language, need_path=True)
        # Get enable distributed dnn training
        distributed = hasattr(automl_settings_obj, "enable_distributed_dnn_training") and \
            automl_settings_obj.enable_distributed_dnn_training is True and has_horovod

        # Set Defaults
        ner_dir = create_unique_dir(DataLiterals.NER_DATA_DIR)
        output_dir = OutputLiterals.OUTPUT_DIR
        labels_filename = OutputLiterals.LABELS_FILE

        # set run properties
        prepare_run_properties(current_run, model_name)

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Save and load dataset
        train_dataset, eval_dataset, label_list = load_and_validate_dataset(
            workspace,
            ner_dir,
            output_dir,
            labels_filename,
            tokenizer,
            automl_settings,
            mltable_data_json,
            is_labeling_run
        )

        # Train model
        trainer = NERPytorchTrainer(
            label_list,
            model_name,
            download_dir,
            output_dir,
            enable_distributed=distributed
        )
        trainer.train(train_dataset)

        if is_main_process():
            tokenizer.save_pretrained(output_dir)

            # Validate model if validation dataset is provided
            primary_metric_score = np.nan
            if eval_dataset:
                results = trainer.validate(eval_dataset)
                # Log results
                log_metrics(current_run, results)
                primary_metric_score = results[primary_metric]

            input_sample_str = "\"This\\nis\\nan\\nexample\""
            output_sample_str = "\"This O\\nis O\\nan O\\n example B-OBJ\""

            # Convert sample strings to np array (every item in conll file is one sample) to meet mlflow contract
            input_mlflow_str = data_transformation._get_data_snapshot(np.array([input_sample_str], dtype=str))
            output_mlflow_str = data_transformation._get_output_snapshot(np.array([output_sample_str], dtype=str))

            model_wrapper = ModelWrapper(trainer.trainer.model, label_list, tokenizer)
            model_path = save_model_wrapper(run=current_run, model=model_wrapper,
                                            save_mlflow=automl_settings_obj.save_mlflow,
                                            input_sample_str=input_mlflow_str,
                                            output_sample_str=output_mlflow_str)

            # Save scoring script
            ner_write_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "io", "write")
            save_script(OutputLiterals.SCORE_SCRIPT, ner_write_dir)

            deploy_script_path = save_deploy_script(ScoringLiterals.NER_SCORE_FILE,
                                                    input_sample_str,
                                                    output_sample_str,
                                                    "StandardPythonParameterType")
            conda_file_path = save_conda_yml(current_run.get_environment())

            prepare_post_run_properties(current_run,
                                        model_path,
                                        2147483648,
                                        conda_file_path,
                                        deploy_script_path,
                                        primary_metric,
                                        primary_metric_score)
    except Exception as e:
        _logger.error("NER runner script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(current_run, scrub_system_exception(e), update_run_properties=True)
        raise
