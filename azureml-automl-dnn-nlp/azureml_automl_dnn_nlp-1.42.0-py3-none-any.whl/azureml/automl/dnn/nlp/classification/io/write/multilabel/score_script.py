# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Score text dataset from model produced by training run."""

import argparse
import logging

from azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer import MultilabelInferencer
from azureml.automl.dnn.nlp.common._utils import get_default_device, get_run_by_id, make_arg, set_logging_parameters
from azureml.automl.dnn.nlp.common.constants import ScoringLiterals
from azureml.train.automl.constants import Tasks

logger = logging.getLogger(__name__)


def main():
    """Wrapper method to execute script only when called and not when imported."""
    parser = argparse.ArgumentParser()
    parser.add_argument(make_arg(ScoringLiterals.RUN_ID),
                        help='run id of the experiment that generated the model')
    parser.add_argument(make_arg(ScoringLiterals.EXPERIMENT_NAME),
                        help='experiment that ran the run which generated the model')
    parser.add_argument(make_arg(ScoringLiterals.OUTPUT_FILE),
                        help='path to output file')
    parser.add_argument(make_arg(ScoringLiterals.INPUT_DATASET_ID),
                        help='id of the dataset to perform batch predictions')
    parser.add_argument(make_arg(ScoringLiterals.INPUT_MLTABLE_URI),
                        help='uri of the MLTable to perform batch predictions')
    parser.add_argument(make_arg(ScoringLiterals.LOG_OUTPUT_FILE_INFO),
                        help='log output file debug info', type=bool, default=False)
    parser.add_argument(make_arg(ScoringLiterals.ENABLE_DATAPOINT_ID_OUTPUT),
                        help='inference output will contain only datapoint ID and predictions',
                        type=bool, default=False)

    args, unknown = parser.parse_known_args()
    if unknown:
        logger.info("Got unknown args, will ignore them")

    task_type = Tasks.TEXT_CLASSIFICATION_MULTILABEL
    set_logging_parameters(task_type, args)

    device = get_default_device()

    train_run = get_run_by_id(args.run_id, args.experiment_name)

    inferencer = MultilabelInferencer(run=train_run, device=device)
    inferencer.score(
        input_dataset_id=args.input_dataset_id,
        input_mltable_uri=args.input_mltable_uri,
        enable_datapoint_id_output=args.enable_datapoint_id_output
    )

    return


if __name__ == "__main__":
    # Execute only if run as a script
    main()
