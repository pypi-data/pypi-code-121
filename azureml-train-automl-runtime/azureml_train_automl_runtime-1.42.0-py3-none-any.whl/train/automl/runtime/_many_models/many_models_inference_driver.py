# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import cast, List, Optional
import datetime
import hashlib
import joblib
import json
import os
import pandas as pd

from azureml.core import Run
from azureml.core.model import Model
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.train.automl.constants import InferenceTypes
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase
from azureml.train.automl.runtime._many_models.utilities import Arguments


class ManyModelsInferenceDriver(AutoMLPRSDriverBase):
    OUTPUT_DIR = "output"

    def __init__(
            self,
            current_step_run: Run,
            args: Arguments
    ):
        """
        This class is used for doing batch inference.

        :param current_step_run: Current step run object, parent of AutoML run.
        :param args: The arguments for the run.
        """
        super(ManyModelsInferenceDriver, self).__init__(current_step_run)
        self.target_column_name = args.target_column_name
        self.time_column_name = args.time_column_name
        self.train_run_id = args.train_run_id
        self.forecast_quantiles = args.forecast_quantiles
        self.partition_column_names = cast(List[str], args.partition_column_names)
        self.inference_type = args.inference_type or InferenceTypes.FORECAST
        self._console_writer.println(f"target_column_name: {self.target_column_name}")
        self._console_writer.println(f"time_column_name: {self.time_column_name}")
        self._console_writer.println(f"train_run_id: {self.train_run_id}")
        self._console_writer.println(f"forecast_quantiles: {self.forecast_quantiles}")

    def run(self, input_data_file: str, output_data_path: str) -> pd.DataFrame:
        """
        Perform batch inference on specified partition(s) of data

        :param input_data_file: Input dataframe or file.
        :param output_data_path: The output path of the data.
        """
        # 1.0 Set up Logging
        self._console_writer.println('Making predictions')
        os.makedirs(os.path.join(".", ManyModelsInferenceDriver.OUTPUT_DIR), exist_ok=True)

        all_predictions = pd.DataFrame()
        date1 = datetime.datetime.now()
        self._console_writer.println(f'starting {str(date1)}')

        # 2.0 Do inference
        self._console_writer.println(input_data_file)
        data = self.read_input_data(input_data_file)
        data = self._do_inference(data)
        all_predictions = all_predictions.append(data)

        # 3.0 Log the run
        date2 = datetime.datetime.now()
        self._console_writer.println(f'ending {str(date2)}')

        self._console_writer.println(str(all_predictions.head()))
        all_predictions.to_parquet(output_data_path)
        return output_data_path

    def _do_inference(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform inference on the dataframe.

        :param data: Input dataframe to make predictions on.
        :return: The dataframe contains the results.
        """
        tags_dict = {}
        for column_name in self.partition_column_names:
            tags_dict.update(
                {column_name: str(data.iat[0, data.columns.get_loc(column_name)])})

        self._console_writer.println(str(tags_dict))

        model_string = '_'.join(str(v) for k, v in sorted(
            tags_dict.items()) if k in self.partition_column_names)
        self._console_writer.println(f"model string to encode {model_string}")
        sha = hashlib.sha256()
        sha.update(model_string.encode())
        model_name = 'automl_' + sha.hexdigest()
        self._console_writer.println(model_name)
        ws = self.current_step_run.experiment.workspace

        model_tags = []
        if self.train_run_id:
            model_tags.append(['RunId', self.train_run_id])

        self._console_writer.println(f'query the model {model_name}')
        model_list = Model.list(ws, name=model_name,
                                tags=model_tags, latest=True)

        if not model_list:
            self._console_writer.println("Could not find model")
            return
        self._console_writer.println(f'Got {len(model_list)} models')

        # Un-pickle model and make predictions
        model_path = model_list[0].download(exist_ok=True)
        model = joblib.load(model_path)
        model_name = model_list[0].name
        self._console_writer.println(f'Unpickled the model {model_name}')

        X_test = data.copy()
        if self.target_column_name is not None:
            X_test.pop(self.target_column_name)

        self._console_writer.println("prediction data head")
        self._console_writer.println(str(X_test.head()))
        predicted_column_name = 'Predictions'
        if self.inference_type == InferenceTypes.FORECAST:
            if self.forecast_quantiles:
                Contract.assert_true(
                    hasattr(model, 'forecast_quantiles'),
                    message=f"model {type(model).__name__} doesn't expose forecast_quantiles method",
                    log_safe=True)
                self._console_writer.println('Inference using forecast quantiles')
                model.quantiles = self.forecast_quantiles
                y_predictions = model.forecast_quantiles(X_test, ignore_data_errors=True)
                data = data.join(y_predictions[model.quantiles])
                data.columns = [str(col) for col in data.columns]
            else:
                Contract.assert_true(
                    hasattr(model, 'forecast'),
                    message=f"model {type(model).__name__} doesn't expose forecast method",
                    log_safe=True)
                self._console_writer.println('Inference using forecast')
                y_predictions, X_trans = model.forecast(X_test, ignore_data_errors=True)
                # Insert predictions to test set
                data[predicted_column_name] = y_predictions
        elif self.inference_type == InferenceTypes.PREDICT_PROBA:
            Contract.assert_true(
                hasattr(model, 'predict_proba'),
                message=f"model {type(model).__name__} doesn't expose predict_proba method",
                log_safe=True)
            self._console_writer.println('Inference using predict_proba')
            y_pred_proba = model.predict_proba(X_test)
            if not isinstance(y_pred_proba, pd.DataFrame):
                y_pred_proba = pd.DataFrame(
                    y_pred_proba, columns=[f"{predicted_column_name}_{x}" for x in range(y_pred_proba.shape[1])])
            data = pd.concat([data, y_pred_proba], axis=1)
        elif self.inference_type == InferenceTypes.PREDICT:
            Contract.assert_true(
                hasattr(model, 'predict'),
                message=f"model {type(model).__name__} doesn't expose predict method",
                log_safe=True)
            self._console_writer.println('Inference using predict')
            y_predictions = model.predict(X_test)
            data[predicted_column_name] = y_predictions
        self._console_writer.println(f'Made predictions {model_name}')
        self._console_writer.println(str(data.head()))
        self._console_writer.println(f'Inserted predictions {model_name}')

        return data
