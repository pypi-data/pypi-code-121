from ast import Call
import asyncio
from audioop import mul
import itertools
from logging import Logger
import logging
from multiprocessing.dummy import Pool
from optparse import Option
from typing import Any, Callable, Coroutine, Dict, Generic, List, Optional, Tuple, TypeVar, Union, final
from uuid import UUID
import uuid
from py import process
from torch.utils.data import Dataset, random_split
import nest_asyncio
import dill
import pathos.multiprocessing as multiprocessing
from dataclasses import dataclass

from .abstractions.instance_factory import InstanceFactory
from ..evaluation.abstractions.evaluation_metric import EvaluationMetric, EvaluationContext, TModel
from ..training.abstractions.stop_condition import StopCondition, TrainingContext
from ..parameter_tuning.abstractions.objective_function import ObjectiveFunction
from ..modeling.abstractions.model import TInput, TTarget
from ..evaluation.abstractions.evaluation_service import EvaluationService, Score
from ..training.abstractions.training_service import TrainingService
from .abstractions.machine_learning_experimentation_service import MachineLearningExperimentationService, MachineLearningExperimentSettings, MachineLearningExperimentResult, MachineLearningRunResult, MachineLearningRunSettings, InstanceSettings
from .default_instance_factory import DefaultInstanceFactory
from .default_dict_instance_factory import DefaultDictInstanceFactory

nest_asyncio.apply()

TSettings = TypeVar('TSettings', InstanceSettings, Dict[str, InstanceSettings])
TInstance = TypeVar('TInstance')

FactoryAlias = Union[InstanceFactory[TSettings, TInstance], Callable[[TSettings], TInstance]]
ModelFactoryAlias = FactoryAlias[InstanceSettings, TModel]
TrainingServiceFactoryAlias = FactoryAlias[InstanceSettings, TrainingService[TInput, TTarget, TModel]]
EvaluationServiceFactoryAlias = FactoryAlias[InstanceSettings, EvaluationService[TInput, TTarget, TModel]]
TrainingDatasetFactoryAlias = FactoryAlias[Dict[str, InstanceSettings], Dict[str, Dataset[Tuple[TInput, TTarget]]]]
EvaluationDatasetFactoryAlias = FactoryAlias[Dict[str, InstanceSettings], Dict[str, Dataset[Tuple[TInput, TTarget]]]]
EvaluationMetricFactoryAlias = FactoryAlias[Dict[str, InstanceSettings], Dict[str, EvaluationMetric[TInput, TTarget, TModel]]]
ObjectiveFunctionFactoryAlias = FactoryAlias[Dict[str, InstanceSettings], Dict[str, ObjectiveFunction[TInput, TTarget, TModel]]]
StopConditionFactoryAlias = FactoryAlias[Dict[str, InstanceSettings], Dict[str, StopCondition[TInput, TTarget, TModel]]]

@dataclass
class RunCheckpoint:
    id: UUID
    run_settings: MachineLearningRunSettings
    train_run_id: UUID

@dataclass
class ExperimentCheckpoint:
    id: UUID
    name: str
    experiment_settings: MachineLearningExperimentSettings
    runs: Dict[UUID, MachineLearningRunSettings]

class DefaultMachineLearningExperimentationService(MachineLearningExperimentationService[TModel]):
    def __init__(self,
    model_factory: ModelFactoryAlias[TModel], 
    training_service_factory: TrainingServiceFactoryAlias[TInput, TTarget, TModel],
    evaluation_service_factory: EvaluationServiceFactoryAlias[TInput, TTarget, TModel],
    training_dataset_factory: TrainingDatasetFactoryAlias[TInput, TTarget], 
    test_dataset_factory: EvaluationDatasetFactoryAlias[TInput, TTarget],
    evaluation_metric_factory: EvaluationMetricFactoryAlias[TInput, TTarget, TModel],
    objective_function_factory: ObjectiveFunctionFactoryAlias[TInput, TTarget, TModel],
    stop_condition_factory: StopConditionFactoryAlias[TInput, TTarget, TModel],
    event_loop: Optional[asyncio.AbstractEventLoop] = None,
    logger: Optional[Logger] = None, 
    process_pool: Optional[multiprocessing.ProcessPool] = None,
    run_logger_factory: Optional[Callable[[str, UUID, UUID, MachineLearningRunSettings, bool], Logger]] = None,
    experiment_logger_factory: Optional[Callable[[str, UUID, MachineLearningExperimentSettings, bool], Logger]] = None,
    save_run_checkpoint_hook: Optional[Callable[[Logger, RunCheckpoint], None]] = None,
    load_run_checkpoint_hook: Optional[Callable[[Logger, UUID], Optional[RunCheckpoint]]] = None,
    save_experiment_checkpoint_hook: Optional[Callable[[Logger, ExperimentCheckpoint], None]] = None,
    load_experiment_checkpoint_hook: Optional[Callable[[Logger, str, UUID], Optional[ExperimentCheckpoint]]] = None):

        if model_factory is None:
            raise ValueError("model_factory")

        if training_service_factory is None:
            raise ValueError("training_service_factory")

        if evaluation_service_factory is None:
            raise ValueError("evaluation_service_factory")

        if training_dataset_factory is None:
            raise ValueError("training_dataset_factory")

        if test_dataset_factory is None:
            raise ValueError("test_dataset_factory")        
            
        if evaluation_metric_factory is None:
            raise ValueError("evaluation_metric_factory")

        if objective_function_factory is None:
            raise ValueError("objective_function_factory")

        if stop_condition_factory is None:
            raise ValueError("stop_condition_factory")

        self.__logger = logger if not logger is None else logging.getLogger()
        self.__pool: multiprocessing.ProcessPool = process_pool if not process_pool is None else multiprocessing.ProcessPool(4)
        self.__event_loop: asyncio.AbstractEventLoop = event_loop if not event_loop is None else asyncio.get_event_loop()
        self.__run_logger_factory: Callable[[str, UUID, UUID, MachineLearningRunSettings, bool], Logger] = run_logger_factory if not run_logger_factory is None else lambda experiment_name, experiment_id, run_id, settings, continue_run: logging.getLogger(str(run_id))
        self.__experiment_logger_factory: Callable[[str, UUID, MachineLearningExperimentSettings, bool], Logger] = experiment_logger_factory if not experiment_logger_factory is None else lambda experiment_name, uuid, settings, continue_run: logging.getLogger(str(uuid))
        self.__model_factory: ModelFactoryAlias[TModel] = model_factory
        self.__training_service_factory: TrainingServiceFactoryAlias[TInput, TTarget, TModel] = training_service_factory
        self.__evaluation_service_factory: EvaluationServiceFactoryAlias[TInput, TTarget, TModel] = evaluation_service_factory
        self.__training_dataset_factory: TrainingDatasetFactoryAlias[TInput, TTarget] = training_dataset_factory
        self.__test_dataset_factory: EvaluationDatasetFactoryAlias[TInput, TTarget] = test_dataset_factory
        self.__evaluation_metric_factory: EvaluationMetricFactoryAlias[TInput, TTarget, TModel] = evaluation_metric_factory
        self.__objective_function_factory: ObjectiveFunctionFactoryAlias[TInput, TTarget, TModel] = objective_function_factory
        self.__stop_condition_factory: StopConditionFactoryAlias[TModel] = stop_condition_factory

        self.__save_run_checkpoint_hook: Optional[Callable[[Logger, RunCheckpoint], None]] = save_run_checkpoint_hook
        self.__load_run_checkpoint_hook: Optional[Callable[[Logger, UUID], Optional[RunCheckpoint]]] = load_run_checkpoint_hook

        self.__save_experiment_checkpoint_hook: Optional[Callable[[Logger, ExperimentCheckpoint], None]] = save_experiment_checkpoint_hook
        self.__load_experiment_checkpoint_hook: Optional[Callable[[Logger, str, UUID], Optional[ExperimentCheckpoint]]] = load_experiment_checkpoint_hook

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['_DefaultMachineLearningExperimentationService__pool']
        del self_dict['_DefaultMachineLearningExperimentationService__event_loop']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __save_run_checkpoint(self, logger: Logger, checkpoint: RunCheckpoint):
        if not self.__save_run_checkpoint_hook is None:
            logger.info("creating run checkpoint...")

            self.__save_run_checkpoint_hook(logger, checkpoint)

            logger.info("run checkpoint created.")

    def __load_run_checkpoint(self, logger: Logger, id: UUID) -> RunCheckpoint:
        if self.__load_run_checkpoint_hook is None:
            return None

        logger.info("Loading last run checkpoint...")

        return self.__load_run_checkpoint_hook(logger, id)

    def __save_experiment_checkpoint(self, logger: Logger, checkpoint: ExperimentCheckpoint):
        if not self.__save_experiment_checkpoint_hook is None:
            logger.info("creating experiment checkpoint...")

            self.__save_experiment_checkpoint_hook(logger, checkpoint)

            logger.info("experiment checkpoint created.")

    def __load_experiment_checkpoint(self, logger: Logger, name: str, id: UUID) -> ExperimentCheckpoint:
        if self.__load_experiment_checkpoint_hook is None:
            return None

        logger.info("Loading last experiment checkpoint...")

        return self.__load_experiment_checkpoint_hook(logger, name, id)

    def execute_run(self, run_settings: MachineLearningRunSettings, experiment_id: Optional[UUID] = None, run_id: Optional[UUID] = None) -> MachineLearningRunResult[TModel]:
        run_id = uuid.uuid4() if run_id is None else run_id

        run_logger: Logger = self.__run_logger_factory(run_settings.experiment_name, experiment_id, run_id, run_settings)

        checkpoint: RunCheckpoint = self.__load_run_checkpoint(run_logger, run_id)

        train_run_id: UUID = None

        if not checkpoint is None:
            train_run_id = checkpoint.train_run_id
            run_settings = checkpoint.run_settings
        else:
            train_run_id = uuid.uuid4()

            new_checkpoint: RunCheckpoint = RunCheckpoint(run_id, run_settings, train_run_id)
            self.__save_run_checkpoint(run_logger, new_checkpoint)

        event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        result: MachineLearningRunResult[TModel] = None

        try:
            run_logger.info("executing run...")

            model: TModel = self.__model_factory(run_settings.model_settings)
            training_service: TrainingService[TInput, TTarget, TModel] = self.__training_service_factory(run_settings.training_service_settings)
            training_datasets: Dict[str, Dataset[Tuple[TInput, TTarget]]] = self.__training_dataset_factory(run_settings.training_dataset_settings)
            stop_conditions: Dict[str, StopCondition[TInput, TTarget, TModel]] =  self.__stop_condition_factory(run_settings.stop_condition_settings)
            objective_functions: Dict[str, ObjectiveFunction[TInput, TTarget, TModel]] = self.__objective_function_factory(run_settings.objective_function_settings)
            evaluation_service: EvaluationService[TInput, TTarget, TModel] = self.__evaluation_service_factory(run_settings.evaluation_service_settings)
            evaluation_datasets: Dict[str, Dataset[Tuple[TInput, TTarget]]] = self.__test_dataset_factory(run_settings.evaluation_dataset_settings)
            evaluation_metrics: Dict[str, EvaluationMetric[TInput, TTarget, TModel]] = self.__evaluation_metric_factory(run_settings.evaluation_metric_settings)
            
            model = event_loop.run_until_complete(training_service.train_on_multiple_datasets(model=model, datasets=training_datasets, stop_conditions=stop_conditions, objective_functions=objective_functions, id=train_run_id))
            scores: Dict[str, Dict[str, Score]] = event_loop.run_until_complete(evaluation_service.evaluate_on_multiple_datasets(model=model, evaluation_datasets=evaluation_datasets, evaluation_metrics=evaluation_metrics))

            result = MachineLearningRunResult[TModel](run_settings=run_settings, model=model, scores=scores)
        except Exception as ex:
            run_logger.exception(msg=ex, exc_info=True, stack_info=True)
        finally:
            run_logger.info("finished run.")
            logging.shutdown()

        return result

    async def run_experiment(self, experiment_settings: MachineLearningExperimentSettings, experiment_id: Optional[UUID] = None) -> MachineLearningExperimentResult[TModel]:
        experiment_id: UUID = uuid.uuid4() if experiment_id is None else experiment_id
        experiment_logger: Logger = self.__experiment_logger_factory(experiment_settings.name, experiment_id, experiment_settings, False)

        checkpoint: ExperimentCheckpoint = self.__load_experiment_checkpoint(experiment_logger, experiment_settings.name, experiment_id)

        runs: Dict[UUID, MachineLearningRunSettings] = None

        if not checkpoint is None:
            runs = checkpoint.runs
            experiment_settings = checkpoint.experiment_settings
        else:
            combinations: List[Tuple] = itertools.product(experiment_settings.model_settings, experiment_settings.training_service_settings, 
            experiment_settings.evaluation_service_settings, experiment_settings.evaluation_dataset_settings, experiment_settings.training_dataset_settings,  
            experiment_settings.evaluation_metric_settings, experiment_settings.objective_function_settings, experiment_settings.stop_condition_settings)

            runs = {uuid.uuid4(): MachineLearningRunSettings(experiment_settings.name, *combination) for combination in combinations}

            new_checkpoint: ExperimentCheckpoint = ExperimentCheckpoint(experiment_id, experiment_settings.name, experiment_settings, runs)
            self.__save_experiment_checkpoint(experiment_logger, new_checkpoint)

        experiment_logger.info(f"running experiment {experiment_settings.name}...")

        result: MachineLearningExperimentResult[TModel] = None

        try:
            results: List[MachineLearningRunResult[TModel]] = self.__pool.map(self.execute_run, [settings for run_id, settings in runs.items()], [experiment_id for run_id, settings in runs.items()], [run_id for run_id, settings in runs.items()])

            result = MachineLearningExperimentResult[TModel](results)
        except Exception as ex:
            experiment_logger.critical(msg=ex, exc_info=True, stack_info=True)
        finally:
            experiment_logger.info(f"finished experiment {experiment_settings.name}.")

        return result

    async def __run_experiment(self, experiment_settings: Tuple[str, MachineLearningExperimentSettings]) -> Tuple[str, MachineLearningExperimentResult[TModel]]:
        result = await self.run_experiment(experiment_settings[1])

        return (experiment_settings[0], result)

    async def run_experiments(self, experiment_settings: Dict[str, MachineLearningExperimentSettings]) -> Dict[str, MachineLearningExperimentResult[TModel]]:
        self.__logger.info(f"running {len(experiment_settings)} experiments...")
        
        experiment_tasks: List[Coroutine[Any, Any, Tuple[str, MachineLearningExperimentResult[TModel]]]] = [self.__run_experiment(settings) for settings in experiment_settings.items()]

        results: List[Tuple[str, MachineLearningExperimentResult[TModel]]] = await asyncio.gather(*experiment_tasks)

        result:  Dict[str, MachineLearningExperimentResult[TModel]] = dict(results)

        self.__logger.info(f"finished all {len(experiment_settings)} experiments")

        return result