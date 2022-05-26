# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Score images from model produced by another run."""

import argparse
import logging

from azureml.automl.dnn.nlp.common._utils import make_arg, set_logging_parameters
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, ScoringLiterals
from azureml.automl.dnn.nlp.ner.inference.score import score
from azureml.train.automl import constants

logger = logging.getLogger(__name__)


def main():
    """Execute script only when called and not when imported."""
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

    args, unknown = parser.parse_known_args()
    if unknown:
        logger.info("Got unknown args, will ignore them")

    task_type = constants.Tasks.TEXT_NER
    set_logging_parameters(task_type, args)

    score(
        run_id=args.run_id,
        input_dataset_id=args.input_dataset_id,
        input_mltable_uri=args.input_mltable_uri,
        data_dir=DataLiterals.NER_DATA_DIR,
        output_dir=OutputLiterals.OUTPUT_DIR
    )


if __name__ == "__main__":
    # Execute only if run as a script
    main()
