import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from transformers import Trainer
from transformers.integrations import rewrite_logs
from transformers.trainer_callback import TrainerCallback
from transformers.utils import flatten_dict

import mlfoundry as mlf
from mlfoundry.mlfoundry_run import MlFoundryRun

__all__ = ["HF_MODEL_PATH", "MlFoundryTrainerCallback"]

logger = logging.getLogger(__name__)

HF_ARTIFACTS_PATH = "hf/"
HF_MODELS_PATH = os.path.join(HF_ARTIFACTS_PATH, "models")
HF_MODEL_PATH = os.path.join(
    HF_MODELS_PATH, "model"
)  # intended to be imported while loading back the model


# TODO: Allow disabling logging via environment variable
# TODO: Allow configuring settings from env
# TODO: Add support for state.is_hyper_param_search
class MlFoundryTrainerCallback(TrainerCallback):
    """
    Huggingface Transformers Trainer Callback for tracking training run on MLFoundry

    Examples:

        ```
        import os
        os.environ["MLF_API_KEY"] = "..."

        from transformers import TrainingArguments, Trainer
        from mlfoundry.integrations.transformers import MlFoundryTrainerCallback

        mlf_cb = MlFoundryTrainerCallback(
            project_name="huggingface",
            run_name="my-hf-run",
            flatten_params=True,
            log_model=True,
        )

        args = TrainingArguments(..., report_to=[])
        trainer = Trainer(..., args=args, callbacks=[mlf_cb])
        trainer.train()
        ```

        Callback can also be created from an existing run

        ```
        import os
        os.environ["MLF_API_KEY"] = "..."

        from transformers import TrainingArguments, Trainer
        import mlfoundry as mlf
        from mlfoundry.integrations.transformers import MlFoundryTrainerCallback

        client = mlf.get_client()
        run = client.create_run(project_name="huggingface")

        mlf_cb = MlFoundryTrainerCallback.from_run(
            run=run,
            auto_end_run=False,
            flatten_params=True,
            log_model=True,
        )

        args = TrainingArguments(..., report_to=[])
        trainer = Trainer(..., args=args, callbacks=[mlf_cb])
        trainer.train()

        run.end()
        ```
    """

    def __init__(
        self,
        project_name: str,
        run_name: Optional[str] = None,
        flatten_params: bool = False,
        log_model: bool = False,
        **kwargs,
    ):
        """
        Args:
            project_name (str): name of the project to create the run under
            run_name (Optional[str], optional): name of the run. When not provided a run name is automatically generated
            flatten_params (bool, optional): if to flatten the args and model config dictionaries before logging them,
                By default, this is `False`

                e.g. when set to True,
                config = {"id2label": {"0": "hello", "1": "bye"}} will be logged as two parameters as
                {"config/id2label.0": "hello", "config/id2label.1": "bye"}
                when set to False,
                config = {"id2label": {"0": "hello"}} will be logged as a single parameter as
                {"config/id2label": '{"0": "hello", "1": "bye"}'}
            log_model (bool, optional): if to log the generated model artifacts at the end of training. By default,
                this is `False`. Note this logs the model at the end of training. This model will be the best model
                according to configured metrics if `load_best_model_at_end` is set to `True` in
                `transformers.training_args.TrainingArguments` passed to the Trainer instance, otherwise this model
                will be the latest model obtained after running all epochs (or steps).
                This model will be logged at `mlf/huggingface_models/model/` path under the run
            **kwargs:
        """
        self._project_name = project_name
        self._run_name = run_name
        self._run = None
        self._auto_end_run = True

        self._flatten_params = flatten_params
        self._log_model = log_model
        self._MAX_PARAM_VAL_LENGTH = 250
        self._MAX_PARAMS_TAGS_PER_BATCH = 100
        self._initialized = False

    @classmethod
    def from_run(
        cls,
        run: MlFoundryRun,
        auto_end_run: bool = False,
        flatten_params: bool = False,
        log_model: bool = False,
        **kwargs,
    ) -> "MlFoundryTrainerCallback":
        """
        Create a MLFoundry Huggingface Transformers Trainer callback from an existing MLFoundry run instance

        Args:
            run (MlFoundryRun): `MlFoundry` run instance
            auto_end_run (bool, optional): if to end the run when training finishes. By default, this is `False`
            flatten_params (bool, optional): if to flatten the args and model config dictionaries before logging them,
                By default, this is `False`

                e.g. when set to True,
                config = {"id2label": {"0": "hello", "1": "bye"}} will be logged as two parameters as
                {"config/id2label.0": "hello", "config/id2label.1": "bye"}
                when set to False,
                config = {"id2label": {"0": "hello"}} will be logged as a single parameter as
                {"config/id2label": '{"0": "hello", "1": "bye"}'}
            log_model (bool, optional): if to log the generated model artifacts at the end of training. By default,
                this is `False`. Note this logs the model at the end of training. This model will be the best model
                according to configured metrics if `load_best_model_at_end` is set to `True` in
                `transformers.training_args.TrainingArguments` passed to the Trainer instance, otherwise this model
                will be the latest model obtained after running all epochs (or steps).
                This model will be logged at `mlf/huggingface_models/model/` path under the run
            **kwargs: Additional keyword arguments to pass to init

        Returns:
            MlFoundryTrainerCallback: an instance of `MlFoundryTrainerCallback`
        """
        instance = cls(
            project_name=run.project_name,
            run_name=run.run_name,
            flatten_params=flatten_params,
            log_model=log_model,
            **kwargs,
        )
        instance._run = run
        instance._auto_end_run = auto_end_run
        return instance

    def setup(self, args, state, model, **kwargs):
        if not state.is_world_process_zero:
            # If the current process is not the global main process in a distributed training setting do nothing
            return

        logger.info("Automatic MLFoundry logging enabled")

        if not self._run:
            self._auto_end_run = True
            self._run = mlf.get_client().create_run(
                project_name=self._project_name,
                run_name=self._run_name,
            )

        args_dict = {f"args/{k}": v for k, v in args.to_dict().items()}
        if self._flatten_params:
            args_dict = flatten_dict(args_dict)

        if hasattr(model, "config") and model.config is not None:
            model_config_dict = {
                f"config/{k}": v for k, v in model.config.to_dict().items()
            }
            if self._flatten_params:
                model_config_dict = flatten_dict(model_config_dict)
        else:
            model_config_dict = {}

        params: Dict[str, Any] = {**args_dict, **model_config_dict}
        for name, value in list(params.items()):
            # internally, all values are converted to str
            if len(str(value)) > self._MAX_PARAM_VAL_LENGTH:
                logger.warning(
                    f'Trainer is attempting to log a value of "{value}" for key "{name}" as a parameter. '
                    f"MlFoundry's log_params() only accepts values no longer than {self._MAX_PARAM_VAL_LENGTH} "
                    f"characters so we dropped this attribute. Pass `flatten_params=True` during init to "
                    f"flatten the parameters and avoid this message."
                )
                del params[name]

        # MlFoundry cannot log more than 100 values in one go, so we have to split it
        params_items: List[Tuple[str, Any]] = list(params.items())
        for i in range(0, len(params_items), self._MAX_PARAMS_TAGS_PER_BATCH):
            self._run.log_params(
                dict(params_items[i : i + self._MAX_PARAMS_TAGS_PER_BATCH])
            )
        self._initialized = True

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        """
        Event called at the beginning of training.
        """
        if not self._initialized:
            self.setup(args, state, model)

    def on_train_end(self, args, state, control, model=None, tokenizer=None, **kwargs):
        """
        Event called at the end of training.
        """
        if self._initialized and state.is_world_process_zero:
            if self._log_model:
                # TODO (chiragjn): this might crash if `on_train_end` is called twice? because we are using a static
                #                  artifacts path
                logger.info("Logging artifacts. This may take time.")
                # We are saving it separately because `model` is the best/latest model, otherwise
                # args.output_dir has all checkpoints based on save strategy
                # TODO (chiragjn): Maybe add support for logging more than one checkpoint
                fake_trainer = Trainer(args=args, model=model, tokenizer=tokenizer)
                with tempfile.TemporaryDirectory() as temp_dir:
                    fake_trainer.save_model(temp_dir)
                    self._run.log_artifact(
                        local_path=temp_dir, artifact_path=HF_MODEL_PATH
                    )
            if self._auto_end_run and self._run:
                self._run.end()

    def on_log(self, args, state, control, model=None, logs=None, **kwargs):
        """
        Event called after logging the last logs.
        """
        if not self._initialized:
            self.setup(args, state, model)
        if not state.is_world_process_zero:
            return
        logs = rewrite_logs(logs)
        metrics = {}
        for k, v in logs.items():
            if isinstance(v, (int, float, np.integer, np.floating)):
                metrics[k] = v
            else:
                logger.warning(
                    f'Trainer is attempting to log a value of "{v}" of type {type(v)} for key "{k}" as a metric. '
                    f"MlFoundry's log_metric() only accepts float and int types so we dropped this attribute."
                )
        self._run.log_metrics(metric_dict=metrics, step=state.global_step)

    def __del__(self):
        if self._auto_end_run and self._run:
            self._run.end()
