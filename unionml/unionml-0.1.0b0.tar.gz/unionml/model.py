"""Model class for defining training, evaluation, and prediction."""

import inspect
import os
from collections import OrderedDict
from dataclasses import asdict, dataclass, field, is_dataclass, make_dataclass
from functools import partial
from inspect import Parameter, signature
from typing import IO, Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Type, Union

import joblib
import sklearn
from dataclasses_json import dataclass_json
from fastapi import FastAPI
from flytekit import Workflow
from flytekit.configuration import Config
from flytekit.core.tracker import TrackedInstance
from flytekit.remote import FlyteRemote
from flytekit.remote.executions import FlyteWorkflowExecution

from unionml.dataset import Dataset
from unionml.utils import inner_task, is_keras_model, is_pytorch_model


@dataclass
class BaseHyperparameters:
    """Hyperparameter base class"""

    pass


class ModelArtifact(NamedTuple):
    """Model artifact, containing a specific model object and optional metrics associated with it."""

    model_object: Any
    hyperparameters: Optional[Union[BaseHyperparameters, dict]] = None
    metrics: Optional[Dict[str, float]] = None


class Model(TrackedInstance):
    def __init__(
        self,
        name: str = "model",
        init: Union[Type, Callable] = None,
        *,
        dataset: Dataset,
        hyperparameter_config: Optional[Dict[str, Type]] = None,
    ):
        super().__init__()
        self.name = name
        self._init_callable = init
        self._hyperparameter_config = hyperparameter_config
        self._dataset = dataset
        self._artifact: Optional[ModelArtifact] = None

        # default component functions
        self._init = self._default_init
        self._saver = self._default_saver
        self._loader = self._default_loader

        # properties needed for deployment
        self._image_name: Optional[str] = None
        self._config_file: Optional[str] = None
        self._registry: Optional[str] = None
        self._dockerfile: Optional[str] = None
        self._project: Optional[str] = None
        self._domain: Optional[str] = None
        self.__remote__: Optional[FlyteRemote] = None

        if self._dataset.name is None:
            self._dataset.name = f"{self.name}.dataset"

        # unionml-compiled tasks
        self._train_task = None
        self._predict_task = None
        self._predict_from_features_task = None

        # user-provided task kwargs
        self._train_task_kwargs = None
        self._predict_task_kwargs = None

        # dynamically defined types
        self._hyperparameter_type: Optional[Type] = None

    @property
    def artifact(self) -> Optional[ModelArtifact]:
        return self._artifact

    @artifact.setter
    def artifact(self, new_value: ModelArtifact):
        self._artifact = new_value

    @property
    def hyperparameter_type(self) -> Type:
        if self._hyperparameter_type is not None:
            return self._hyperparameter_type

        hyperparameter_fields: List[Any] = []
        if self._hyperparameter_config is None:
            # extract types from the init callable that instantiates a new model
            model_obj_sig = signature(self._init_callable)  # type: ignore

            # if any of the arguments are not type-annotated, default to using an untyped dictionary
            if any(p.annotation is inspect._empty for p in model_obj_sig.parameters.values()):
                return dict

            for hparam_name, hparam in model_obj_sig.parameters.items():
                hyperparameter_fields.append((hparam_name, hparam.annotation, field(default=hparam.default)))
        else:
            # extract types from hyperparameters Model init argument
            for hparam_name, hparam_type in self._hyperparameter_config.items():
                hyperparameter_fields.append((hparam_name, hparam_type))

        self._hyperparameter_type = dataclass_json(
            make_dataclass("Hyperparameters", hyperparameter_fields, bases=(BaseHyperparameters,))
        )
        return self._hyperparameter_type

    @property
    def config_file(self) -> Optional[str]:
        return self._config_file

    @property
    def registry(self) -> Optional[str]:
        return self._registry

    @property
    def dockerfile(self) -> Optional[str]:
        return self._dockerfile

    @property
    def train_workflow_name(self):
        return f"{self.name}.train"

    @property
    def predict_workflow_name(self):
        return f"{self.name}.predict"

    @property
    def predict_from_features_workflow_name(self):
        return f"{self.name}.predict_from_features"

    def init(self, fn):
        self._init = fn
        return self._init

    def trainer(self, fn=None, **train_task_kwargs):
        if fn is None:
            return partial(self.trainer, **train_task_kwargs)
        self._trainer = fn
        self._train_task_kwargs = train_task_kwargs
        return self._trainer

    def predictor(self, fn=None, **predict_task_kwargs):
        if fn is None:
            return partial(self.predictor, **predict_task_kwargs)
        self._predictor = fn
        self._predict_task_kwargs = predict_task_kwargs
        return self._predictor

    def evaluator(self, fn):
        self._evaluator = fn
        return self._evaluator

    def saver(self, fn):
        self._saver = fn
        return self._saver

    def loader(self, fn):
        self._loader = fn
        return self._loader

    @property
    def trainer_params(self):
        return {
            name: param
            for name, param in signature(self._trainer).parameters.items()
            if param.kind == Parameter.KEYWORD_ONLY
        }

    def train_workflow(self):
        dataset_task = self._dataset.dataset_task()
        train_task = self.train_task()

        [
            hyperparam_arg,
            hyperparam_type,
        ], *_ = train_task.python_interface.inputs.items()

        wf = Workflow(name=self.train_workflow_name)

        # add hyperparameter argument
        wf.add_workflow_input(hyperparam_arg, hyperparam_type)

        # add dataset.reader arguments
        for arg, type in dataset_task.python_interface.inputs.items():
            wf.add_workflow_input(arg, type)

        # add training keyword-only arguments
        trainer_param_types = {k: v.annotation for k, v in self.trainer_params.items()}
        for arg, type in trainer_param_types.items():
            wf.add_workflow_input(arg, type)

        dataset_node = wf.add_entity(
            dataset_task,
            **{k: wf.inputs[k] for k in dataset_task.python_interface.inputs},
        )
        train_node = wf.add_entity(
            train_task,
            **{
                hyperparam_arg: wf.inputs[hyperparam_arg],
                **dataset_node.outputs,
                **{arg: wf.inputs[arg] for arg in trainer_param_types},
            },
        )
        wf.add_workflow_output("model_object", train_node.outputs["model_object"])
        wf.add_workflow_output("hyperparameters", train_node.outputs["hyperparameters"])
        wf.add_workflow_output("metrics", train_node.outputs["metrics"])
        return wf

    def predict_workflow(self):
        dataset_task = self._dataset.dataset_task()
        predict_task = self.predict_task()

        wf = Workflow(name=self.predict_workflow_name)
        model_arg_name, *_ = predict_task.python_interface.inputs.keys()
        wf.add_workflow_input("model_object", predict_task.python_interface.inputs[model_arg_name])
        for arg, type in dataset_task.python_interface.inputs.items():
            wf.add_workflow_input(arg, type)

        dataset_node = wf.add_entity(
            dataset_task,
            **{k: wf.inputs[k] for k in dataset_task.python_interface.inputs},
        )
        predict_node = wf.add_entity(
            predict_task, **{"model_object": wf.inputs["model_object"], **dataset_node.outputs}
        )
        for output_name, promise in predict_node.outputs.items():
            wf.add_workflow_output(output_name, promise)
        return wf

    def predict_from_features_workflow(self):
        predict_task = self.predict_from_features_task()

        wf = Workflow(name=self.predict_from_features_workflow_name)
        for i, (arg, type) in enumerate(predict_task.python_interface.inputs.items()):
            # assume that the first argument is the model object
            wf.add_workflow_input("model_object" if i == 0 else arg, type)

        predict_node = wf.add_entity(predict_task, **{k: wf.inputs[k] for k in wf.inputs})
        for output_name, promise in predict_node.outputs.items():
            wf.add_workflow_output(output_name, promise)
        return wf

    def train_task(self):
        if self._train_task:
            return self._train_task

        # make sure hyperparameter type signature is correct
        *_, hyperparameters_param = signature(self._init).parameters.values()
        hyperparameters_param = hyperparameters_param.replace(annotation=self.hyperparameter_type)

        # assume that reader_return_type is a dict with only a single entry
        [(data_arg_name, data_arg_type)] = self._dataset.reader_return_type.items()

        # get keyword-only training args
        @inner_task(
            unionml_obj=self,
            input_parameters=OrderedDict(
                [
                    (p.name, p)
                    for p in [
                        hyperparameters_param,
                        Parameter(
                            data_arg_name,
                            kind=Parameter.KEYWORD_ONLY,
                            annotation=data_arg_type,
                        ),
                        *self.trainer_params.values(),
                    ]
                ]
            ),
            return_annotation=NamedTuple(
                "ModelArtifact",
                model_object=signature(self._trainer).return_annotation,
                hyperparameters=self.hyperparameter_type,
                metrics=Dict[str, signature(self._evaluator).return_annotation],
            ),
            **({} if self._train_task_kwargs is None else self._train_task_kwargs),
        )
        def train_task(**kwargs):
            hyperparameters = kwargs["hyperparameters"]
            raw_data = kwargs[data_arg_name]
            trainer_kwargs = {p: kwargs[p] for p in self.trainer_params}

            hyperparameters_dict = asdict(hyperparameters) if is_dataclass(hyperparameters) else hyperparameters
            training_data = self._dataset.get_data(raw_data)
            model_object = self._trainer(
                self._init(hyperparameters=hyperparameters_dict),
                *training_data["train"],
                **trainer_kwargs,
            )
            metrics = {
                split_key: self._evaluator(model_object, *training_data[split_key]) for split_key in training_data
            }
            return model_object, hyperparameters, metrics

        self._train_task = train_task
        return train_task

    def predict_task(self):
        if self._predict_task:
            return self._predict_task

        predictor_sig = signature(self._predictor)
        model_param, *_ = predictor_sig.parameters.values()
        model_param = model_param.replace(name="model_object")

        # assume that reader_return_type is a dict with only a single entry
        [(data_arg_name, data_arg_type)] = self._dataset.reader_return_type.items()
        data_param = Parameter(data_arg_name, kind=Parameter.KEYWORD_ONLY, annotation=data_arg_type)

        # TODO: make sure return type is not None
        @inner_task(
            unionml_obj=self,
            input_parameters=OrderedDict([(p.name, p) for p in [model_param, data_param]]),
            return_annotation=predictor_sig.return_annotation,
            **self._predict_task_kwargs,
        )
        def predict_task(model_object, **kwargs):
            parsed_data = self._dataset._parser(kwargs[data_arg_name], **self._dataset.parser_kwargs)
            features = parsed_data[self._dataset._parser_feature_key]
            return self._predictor(model_object, features)

        self._predict_task = predict_task
        return predict_task

    def predict_from_features_task(self):
        if self._predict_from_features_task:
            return self._predict_from_features_task

        predictor_sig = signature(self._predictor)
        model_param, *_ = predictor_sig.parameters.values()
        model_param = model_param.replace(name="model_object")

        # assume that reader_return_type is a dict with only a single entry
        [(_, data_arg_type)] = self._dataset.reader_return_type.items()
        data_param = Parameter("features", kind=Parameter.KEYWORD_ONLY, annotation=data_arg_type)

        @inner_task(
            unionml_obj=self,
            input_parameters=OrderedDict([("model_object", model_param), ("features", data_param)]),
            return_annotation=predictor_sig.return_annotation,
            **self._predict_task_kwargs,
        )
        def predict_from_features_task(model_object, features):
            return self._predictor(model_object, self._dataset.get_features(features))

        self._predict_from_features_task = predict_from_features_task
        return predict_from_features_task

    def train(
        self,
        hyperparameters: Optional[Dict[str, Any]] = None,
        trainer_kwargs: Optional[Dict[str, Any]] = None,
        **reader_kwargs,
    ) -> Tuple[Any, Any]:
        trainer_kwargs = {} if trainer_kwargs is None else trainer_kwargs
        model_obj, hyperparameters, metrics = self.train_workflow()(
            hyperparameters=self.hyperparameter_type(**({} if hyperparameters is None else hyperparameters)),
            **{**reader_kwargs, **trainer_kwargs},
        )
        self.artifact = ModelArtifact(model_obj, hyperparameters, metrics)
        return model_obj, metrics

    def predict(
        self,
        features: Any = None,
        **reader_kwargs,
    ):
        if self.artifact is None:
            raise RuntimeError(
                "ModelArtifact not found. You must train a model first with the `train` method before generating "
                "predictions."
            )
        if features is None:
            return self.predict_workflow()(model_object=self.artifact.model_object, **reader_kwargs)
        return self.predict_from_features_workflow()(model_object=self.artifact.model_object, features=features)

    def save(self, file, *args, **kwargs):
        if self.artifact is None:
            raise AttributeError("`artifact` property is None. Call the `train` method to train a model first")
        return self._saver(self.artifact.model_object, self.artifact.hyperparameters, file, *args, **kwargs)

    def load(self, file, *args, **kwargs):
        return self._loader(file, *args, **kwargs)

    def serve(self, app: FastAPI, remote: bool = False, model_version: str = "latest"):
        """Create a FastAPI serving app."""
        from unionml.fastapi import serving_app

        serving_app(self, app, remote=remote, model_version=model_version)

    def remote(
        self,
        registry: Optional[str] = None,
        image_name: str = None,
        dockerfile: str = "Dockerfile",
        config_file: Optional[str] = None,
        project: Optional[str] = None,
        domain: Optional[str] = None,
    ):
        self._config_file = config_file
        self._registry = registry
        self._image_name = image_name
        self._dockerfile = dockerfile
        self._project = project
        self._domain = domain

    @property
    def _remote(self) -> Optional[FlyteRemote]:
        if self.__remote__ is not None:
            return self.__remote__

        config = Config.auto(config_file=self._config_file)
        if config.platform.endpoint.startswith("localhost"):
            config = Config.for_sandbox()

        self.__remote__ = FlyteRemote(
            config=config,
            default_project=self._project,
            default_domain=self._domain,
        )
        return self.__remote__

    def remote_deploy(self):
        """Deploy model services to a Flyte backend."""
        from unionml import remote

        app_version = remote.get_app_version()
        image = remote.get_image_fqn(self, app_version, self._image_name)

        os.environ["FLYTE_INTERNAL_IMAGE"] = image or ""
        _remote = self._remote

        remote.create_project(_remote, self._project)
        if _remote.config.platform.endpoint.startswith("localhost"):
            # assume that a localhost flyte_admin_url means that we want to use Flyte sandbox
            remote.sandbox_docker_build(self, image)
        else:
            remote.docker_build_push(self, image)

        args = [_remote._default_project, _remote._default_domain, app_version]
        for wf in [
            self.train_workflow(),
            self.predict_workflow(),
            self.predict_from_features_workflow(),
        ]:
            remote.deploy_wf(wf, _remote, image, *args)

    def remote_train(
        self,
        app_version: str = None,
        wait: bool = True,
        *,
        hyperparameters: Optional[Dict[str, Any]] = None,
        trainer_kwargs: Optional[Dict[str, Any]] = None,
        **reader_kwargs,
    ) -> Union[ModelArtifact, FlyteWorkflowExecution]:
        if self._remote is None:
            raise RuntimeError("First configure the remote client with the `Model.remote` method")

        from unionml import remote

        app_version = app_version or remote.get_app_version()
        train_wf = self._remote.fetch_workflow(name=self.train_workflow_name, version=app_version)
        execution = self._remote.execute(
            train_wf,
            inputs={
                "hyperparameters": self.hyperparameter_type(**({} if hyperparameters is None else hyperparameters)),
                **{**reader_kwargs, **({} if trainer_kwargs is None else trainer_kwargs)},  # type: ignore
            },
            project=self._remote.default_project,
            domain=self._remote.default_domain,
            wait=wait,
            type_hints={"hyperparameters": self.hyperparameter_type},
        )
        console_url = self._remote.generate_console_url(execution)
        print(
            f"Executing {train_wf.id.name}, execution name: {execution.id.name}."
            f"\nGo to {console_url} to see the execution in the console."
        )
        if not wait:
            return execution

        self.remote_load(execution)
        return self.artifact

    def remote_predict(
        self,
        app_version: str = None,
        model_version: str = None,
        wait: bool = True,
        *,
        features: Any = None,
        **reader_kwargs,
    ) -> Union[Any, FlyteWorkflowExecution]:
        if self._remote is None:
            raise RuntimeError("First configure the remote client with the `Model.remote` method")

        from unionml import remote

        app_version = app_version or remote.get_app_version()
        model_artifact = remote.get_model_artifact(self, app_version, model_version)

        if (features is not None and len(reader_kwargs) > 0) or (features is None and len(reader_kwargs) == 0):
            raise ValueError("You must provide only one of `features` or `reader_kwargs`")

        inputs = {"model_object": model_artifact.model_object}
        if features is None:
            workflow_name = self.predict_workflow_name
            inputs.update(reader_kwargs)
            type_hints = {}
        else:
            workflow_name = self.predict_from_features_workflow_name
            inputs.update({"features": features})
            type_hints = {"features": [*self._dataset.reader_return_type.values()][0]}

        predict_wf = self._remote.fetch_workflow(
            self._remote._default_project,
            self._remote._default_domain,
            workflow_name,
            app_version,
        )
        execution = self._remote.execute(
            predict_wf,
            inputs=inputs,
            project=self._remote.default_project,
            domain=self._remote.default_domain,
            wait=wait,
            type_hints=type_hints,
        )
        console_url = self._remote.generate_console_url(execution)
        print(
            f"Executing {predict_wf.id.name}, execution name: {execution.id.name}."
            f"\nGo to {console_url} to see the execution in the console."
        )
        if not wait:
            return execution
        predictions, *_ = execution.outputs.values()
        return predictions

    def remote_wait(self, execution: FlyteWorkflowExecution, **kwargs) -> Any:
        if self._remote is None:
            raise ValueError("You must call `model.remote` to attach a remote backend to this model.")
        return self._remote.wait(execution, **kwargs)

    def remote_load(self, execution: FlyteWorkflowExecution):
        if self._remote is None:
            raise ValueError("You must call `model.remote` to attach a remote backend to this model.")
        if not execution.is_done:
            print(f"Waiting for execution {execution.id.name} to complete...")
            execution = self.remote_wait(execution)
            print("Done.")

        with self._remote.remote_context():
            self.artifact = ModelArtifact(
                execution.outputs["model_object"],
                execution.outputs["hyperparameters"],
                execution.outputs["metrics"],
            )

    def remote_list_model_versions(self, app_version: str = None, limit: int = 10) -> List[str]:
        from unionml import remote

        app_version = app_version or remote.get_app_version()
        return remote.list_model_versions(self, app_version=app_version, limit=limit)

    def remote_fetch_predictions(self, execution: FlyteWorkflowExecution) -> Any:
        if self._remote is None:
            raise ValueError("You must call `model.remote` to attach a remote backend to this model.")
        execution = self._remote.wait(execution)
        predictions, *_ = execution.outputs.values()
        return predictions

    def _default_init(self, hyperparameters: dict) -> Any:
        if self._init_callable is None:
            raise ValueError(
                "When using the _default_init method, you must specify the init argument to the Model constructor."
            )
        return self._init_callable(**hyperparameters)

    def _default_saver(
        self,
        model_obj: Any,
        hyperparameters: Union[dict, BaseHyperparameters],
        file: Union[str, os.PathLike, IO],
        *args,
        **kwargs,
    ) -> Any:
        init = self._init_callable if self._init == self._default_init else self._init or self._init_callable
        model_type = init if inspect.isclass(init) else signature(init).return_annotation if init is not None else init
        hyperparameters = asdict(hyperparameters) if is_dataclass(hyperparameters) else hyperparameters
        if isinstance(model_obj, sklearn.base.BaseEstimator):
            return joblib.dump({"model_obj": model_obj, "hyperparameters": hyperparameters}, file, *args, **kwargs)
        elif is_pytorch_model(model_type):
            import torch

            torch.save(
                {"model_obj": model_obj.state_dict(), "hyperparameters": hyperparameters},
                file,
                *args,
                **kwargs,
            )
            return file
        elif is_keras_model(model_type):
            model_obj.save(file, *args, **kwargs)
            return file

        raise NotImplementedError(
            f"Default saver not defined for type {type(model_obj)}. Use the Model.saver decorator to define one."
        )

    def _default_loader(self, file: Union[str, os.PathLike, IO], *args, **kwargs) -> Any:
        init = self._init_callable if self._init == self._default_init else self._init or self._init_callable
        model_type = init if inspect.isclass(init) else signature(init).return_annotation if init is not None else init

        if issubclass(model_type, sklearn.base.BaseEstimator):
            deserialized_model = joblib.load(file, *args, **kwargs)
            return deserialized_model["model_obj"]
        elif is_pytorch_model(model_type):
            import torch

            deserialized_model = torch.load(file, *args, **kwargs)
            model = model_type(**deserialized_model["hyperparameters"])
            model.load_state_dict(deserialized_model["model_obj"])
            return model
        elif is_keras_model(model_type):
            from tensorflow import keras

            return keras.models.load_model(file)

        raise NotImplementedError(
            f"Default loader not defined for type {model_type}. Use the Model.loader decorator to define one."
        )
