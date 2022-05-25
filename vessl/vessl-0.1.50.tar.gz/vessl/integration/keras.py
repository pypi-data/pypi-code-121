from typing import List

import numpy as np
from tensorflow import keras

from vessl.experiment import list_experiments
from vessl.integration.common import get_current_experiment
from vessl.internal import log
from vessl.model import create_model
from vessl.util import logger
from vessl.util.constant import (
    VESSL_LOG_LEVEL,
    VESSL_PLOTS_FILETYPE_IMAGE,
    VESSL_PLOTS_FILETYPE_IMAGES,
)
from vessl.util.exception import InvalidExperimentError, InvalidParamsError
from vessl.util.image import Image


class ExperimentCallback(keras.callbacks.Callback):
    def __init__(
        self,
        data_type=None,
        validation_data=None,
        num_images=None,
        labels=None,
        start_epoch=0,
        save_image=False,
    ):
        super().__init__()
        self._data_type = data_type
        self._num_images = num_images or 1
        self._labels = labels
        self._start_epoch = start_epoch
        self._save_image = save_image

        self.validation_data = None
        if validation_data is not None:
            self.validation_data = validation_data

    def _results_to_predicts(self, results):
        predicts = []
        if results[0].shape[-1] == 1:
            if len(self._labels) == 2:
                predicts = [
                    self._lables[1] if result[0] > 0.5 else self._labels[0]
                    for result in results
                ]
            else:
                if not self._labels:
                    logger.warn("Cannot find labels for prediction")
                predicts = [result[0] for result in results]
        else:
            argmax_results = np.argmax(np.stack(results), axis=1)
            if not self._labels:
                logger.warn("Cannot find labels for prediction")
                predicts = argmax_results
            else:
                for argmax_result in argmax_results:
                    try:
                        predicts.append(self._labels[argmax_result])
                    except IndexError:
                        predicts.append(argmax_result)
        return predicts

    def _inference(self):
        x_val, y_val = self.validation_data

        if self._num_images > len(x_val):
            self._num_images = len(x_val)

        random_indices = np.random.choice(len(x_val), self._num_images, replace=False)
        x_val_random = [x_val[i] for i in random_indices]
        y_val_random = [y_val[i] for i in random_indices]

        results = self.model.predict(np.stack(x_val_random), batch_size=1)
        predicts = self._results_to_predicts(results)

        captions = []
        for predict, truth in zip(predicts, y_val_random):
            captions.append(f"Pred: {predict} Truth: {truth}")

        return [Image(x, caption=caption) for x, caption in zip(x_val_random, captions)]

    def _on_epoch_end(self, epoch, logs=None):
        log(step=epoch + self._start_epoch + 1, payload=logs)

        if self._save_image and self._data_type in (
            VESSL_PLOTS_FILETYPE_IMAGE,
            VESSL_PLOTS_FILETYPE_IMAGES,
        ):
            if self.validation_data is None:
                logger.warn("Cannot find validation_data")

            log({"validation_image": self._inference()})

    def on_epoch_end(self, epoch, logs=None):
        try:
            self._on_epoch_end(epoch, logs)
        except Exception as e:
            exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
            logger.exception(f"{e.__class__.__name__}: {str(e)}", exc_info=exc_info)


MODEL_UPLOAD_POLICY_ALWAYS: str = "always"
MODEL_UPLOAD_POLICY_BEST_ONLY: str = "best_only"
MODEL_UPLOAD_OBJECTIVE_MAXIMIZE: str = "maximize"
MODEL_UPLOAD_OBJECTIVE_MINIMIZE: str = "minimize"


class ModelCallback(keras.callbacks.Callback):
    def __init__(
        self,
        upload_policy: str = MODEL_UPLOAD_POLICY_ALWAYS,
        objective: str = None,
        target_metric: str = None,
        description: str = None,
        tags: List[str] = [],
    ):
        super().__init__()
        if upload_policy not in [
            MODEL_UPLOAD_POLICY_ALWAYS,
            MODEL_UPLOAD_POLICY_BEST_ONLY,
        ]:
            raise InvalidParamsError(
                "upload_policy: should be one of: "
                f"{MODEL_UPLOAD_POLICY_ALWAYS}, {MODEL_UPLOAD_POLICY_BEST_ONLY}"
            )
        if upload_policy == MODEL_UPLOAD_POLICY_BEST_ONLY:
            if objective not in [
                MODEL_UPLOAD_OBJECTIVE_MAXIMIZE,
                MODEL_UPLOAD_OBJECTIVE_MINIMIZE,
            ]:
                raise InvalidParamsError(
                    "objective: should be one of: "
                    f"{MODEL_UPLOAD_OBJECTIVE_MAXIMIZE}, {MODEL_UPLOAD_OBJECTIVE_MINIMIZE}"
                )

        self._upload_policy = upload_policy
        self._objective = objective
        self._target_metric = target_metric
        self._description = description
        self._tags = tags

    def _should_upload_model(self, logs=None) -> bool:
        if self._upload_policy == MODEL_UPLOAD_POLICY_ALWAYS:
            return True

        target_metric_name = self._target_metric
        if target_metric_name not in logs:
            logger.warn(f"metric {target_metric_name} not in train logs: {logs}")
            return False

        # Get previous best model and compare with trained model
        # TODO: compare with previous models rather than experiments
        prev_experiments = list_experiments(
            order_field=f"metrics_summary.latest.{target_metric_name}.value",
            order_direction="desc"
            if self._objective == MODEL_UPLOAD_OBJECTIVE_MAXIMIZE
            else "asc",
            limit=1,
        )
        if len(prev_experiments) == 0:
            # No best model found: upload this model
            return True

        prev_metric = prev_experiments[0].metrics_summary["latest"]
        if target_metric_name not in prev_metric:
            raise InvalidExperimentError(
                f"Expected metric value not found from experiment: {target_metric_name}"
            )
        prev_metric_value = prev_metric[target_metric_name]["value"]
        if (
            self._objective == MODEL_UPLOAD_OBJECTIVE_MAXIMIZE
            and logs[target_metric_name] >= prev_metric_value
        ):
            return True
        if (
            self._objective == MODEL_UPLOAD_OBJECTIVE_MINIMIZE
            and logs[target_metric_name] <= prev_metric_value
        ):
            return True
        return False

    def _on_train_end(self, logs=None):
        experiment = get_current_experiment()
        if experiment is None:
            return

        if self._should_upload_model(logs):
            create_model(
                experiment=experiment.id,
                description=self._description,
                tags=self._tags,
            )

    def on_train_end(self, logs=None):
        try:
            self._on_train_end(logs)
        except Exception as e:
            exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
            logger.exception(f"{e.__class__.__name__}: {str(e)}", exc_info=exc_info)
