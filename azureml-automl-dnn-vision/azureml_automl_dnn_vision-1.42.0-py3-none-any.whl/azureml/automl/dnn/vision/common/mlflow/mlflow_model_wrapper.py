# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper class that loads the Mlflow model, preprocess inputs and performs inference."""

import mlflow
import json
import base64
import tempfile
import pandas as pd
from typing import Any, Callable, Dict
from azureml.automl.core.shared import logging_utilities
from azureml.automl.dnn.vision.common.logging_utils import get_logger

logger = get_logger(__name__)


class MLFlowImagesModelWrapper(mlflow.pyfunc.PythonModel):
    """ MLFlow model wrapper for AutoML for Images models."""

    def __init__(self, task_type: str,
                 scoring_method: Callable[..., None],
                 model_settings: Dict[str, Any]) -> None:
        """This method is called when the python model wrapper is initialized.

        :param model_settings: Settings for the model.
        :type model_settings: dict
        :param task_type: Task type used in training.
        :type task_type: str
        :param scoring_method: scoring function corresponding to the task type.
        :type scoring_method: python method
        """
        super().__init__()
        self._task_type = task_type
        self._scoring_method = scoring_method
        self._model_settings = model_settings

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """This method is called when loading a Mlflow model with pyfunc.load_model().

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        """
        from azureml.automl.dnn.vision.common.model_export_utils import load_model
        with open(context.artifacts["settings"]) as f:
            self._model_settings = json.load(f)
        try:
            self._model = load_model(self._task_type, context.artifacts["model"], **self._model_settings)
        except Exception as e:
            logger.warning("Failed to load the the model.")
            logging_utilities.log_traceback(e, logger)
            raise

    def _decode_base64_img(self, img: pd.Series) -> pd.Series:
        """This method decodes input data from base64 format.
        https://github.com/mlflow/mlflow/blob/master/examples/flower_classifier/image_pyfunc.py

        :param img: pandas series with image in base64 format.
        :type img: pd.Series
        :return: decoded image in pandas series format.
        :rtype: Pandas Series
        """
        return pd.Series(base64.decodebytes(bytearray(img[0])))

    def predict(self, context: mlflow.pyfunc.PythonModelContext, input_data: pd.DataFrame) -> pd.DataFrame:
        """This method performs inference on the input data.

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Input images for prediction.
        :type input_data: Pandas DataFrame with a first column name ['image'] of images where each
        image is in base64 String format.
        :return: Output of inferencing
        :rtype: Pandas DataFrame with columns ['filename', 'probs', 'labels'] for classification and
        ['filename', 'boxes'] for object detection, instance segmentation
        """
        from azureml.automl.dnn.vision.common.model_export_utils import create_temp_file, run_inference_batch

        decoded_images = input_data.apply(axis=1, func=self._decode_base64_img)
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            image_path_list = decoded_images.iloc[:, 0].map(lambda row: create_temp_file(row, tmp_output_dir)).tolist()
            result = run_inference_batch(self._model, image_path_list, self._scoring_method)
        process_result: Callable[[str], Any] = lambda x: json.loads(x)
        return pd.DataFrame(map(process_result, result))
