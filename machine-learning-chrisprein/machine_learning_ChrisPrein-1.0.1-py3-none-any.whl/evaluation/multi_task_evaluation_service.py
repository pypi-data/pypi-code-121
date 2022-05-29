from logging import Logger
import logging
from typing import Any, Callable, Coroutine, TypeVar, List, Generic, Optional, Dict, Tuple, Union
from uuid import UUID
import uuid

from attr import asdict
from ..modeling.abstractions.model import Model, TInput, TTarget
from .abstractions.evaluation_metric import EvaluationContext, EvaluationMetric, Prediction, TModel
from .abstractions.evaluation_service import EvaluationService, Score
from .default_evaluation import default_evaluation
import asyncio
import asyncio.tasks
import asyncio.futures
from dataset_handling.dataloader import DataLoader
from torch.utils.data.dataset import Dataset
import nest_asyncio

nest_asyncio.apply()

class MultiTaskEvaluationService(EvaluationService[TInput, TTarget, TModel]):
    def __init__(self, evaluation_hook: Callable[[Logger, EvaluationContext[TInput, TTarget, TModel], TModel, List[TInput], List[TTarget]], List[TTarget]] = default_evaluation, logger: Optional[Logger]=None, batch_size: int = 1, drop_last: bool = True, event_loop: Optional[asyncio.AbstractEventLoop] = None):
        if evaluation_hook is None:
            raise ValueError("evaluation_hook")
        
        self.__logger = logger if not logger is None else logging.getLogger()
        self.__event_loop: asyncio.AbstractEventLoop = event_loop if not event_loop is None else asyncio.get_event_loop()
        self.__batch_size: int = batch_size
        self.__drop_last: bool = drop_last
        self.__evaluation_hook: Callable[[Logger, EvaluationContext[TInput, TTarget, TModel], TModel, List[TInput], List[TTarget]], List[TTarget]] = evaluation_hook

    def __predict_batch(self, evaluation_context: EvaluationContext[TInput, TTarget, TModel], model: TModel, batch: List[Tuple[TInput, TTarget]]) -> List[Prediction]:
        inputs: List[TInput] = [sample[0] for sample in batch]
        targets: List[TInput] = [sample[1] for sample in batch]
        predictions: List[TTarget] = self.__evaluation_hook(self.__logger, evaluation_context, model, inputs, targets)

        combined: List[Tuple[TInput, TTarget, TTarget]] = zip(inputs, predictions, targets)

        return [Prediction(result[0], result[1], result[2]) for result in combined]

    async def evaluate(self, model: TModel, evaluation_dataset: Union[Tuple[str, Dataset[Tuple[TInput, TTarget]]], Dataset[Tuple[TInput, TTarget]]], evaluation_metrics: Dict[str, EvaluationMetric[TInput, TTarget, TModel]], logger: Optional[Logger] = None) -> Dict[str, Score]:
        if logger is None:
            logger = self.__logger
        
        if model is None:
            raise ValueError("model")

        if evaluation_dataset is None:
            raise ValueError("evaluation_dataset")

        if evaluation_metrics is None:
            raise ValueError("evaluation_metrics")

        dataset: Dataset[Tuple[TInput, TTarget]] = None
        dataset_name: str = None

        if isinstance(evaluation_dataset, Tuple):
            dataset = evaluation_dataset[1]
            dataset_name = evaluation_dataset[0]
        else:
            dataset = evaluation_dataset
            dataset_name = type(dataset).__name__

        evaluation_context: EvaluationContext[TInput, TTarget, TModel] = EvaluationContext[TInput, TTarget, TModel](model, dataset_name, [])

        data_loader: DataLoader[Tuple[TInput, TTarget]] = DataLoader[Tuple[TInput, TTarget]](dataset=dataset, batch_size=self.__batch_size, drop_last=self.__drop_last)

        logger.info('Starting evaluation loop...')

        prediction_futures: List[asyncio.Future] = [self.__event_loop.run_in_executor(None, lambda: self.__predict_batch(evaluation_context, model, batch)) for batch in data_loader]
        predictions: List[List[Prediction]] = await asyncio.gather(*prediction_futures, loop=self.__event_loop)

        for t in predictions:
            evaluation_context.predictions.extend(t) 

        result: Dict[str, Score] = {}

        for i, (name, evaluation_metric) in enumerate(evaluation_metrics.items()):
            value: float = evaluation_metric.calculate_score(context=evaluation_context)

            result[name] = Score[TInput, TTarget](value, evaluation_context.predictions, name, dataset_name)

        logger.info('Finished evaluation loop.')
        logger.info({'evaluation_context': evaluation_context})
        logger.info({'scores': result})

        return result

    async def __evaluate(self, model: TModel, evaluation_dataset: Tuple[str, Dataset[Tuple[TInput, TTarget]]], evaluation_metrics: Dict[str, EvaluationMetric[TInput, TTarget, TModel]], logger: Logger) -> Tuple[str, Dict[str, Score]]:
        result = await self.evaluate(model, evaluation_dataset, evaluation_metrics, logger)

        return (evaluation_dataset[0], result)

    async def evaluate_on_multiple_datasets(self, model: TModel, evaluation_datasets: Dict[str, Dataset[Tuple[TInput, TTarget]]], evaluation_metrics: Dict[str, EvaluationMetric[TInput, TTarget, TModel]]) -> Dict[str, Dict[str, Score]]:
        self.__logger.info(f"starting evaluation on {len(evaluation_datasets)} datasets...")
        
        experiment_tasks: List[Coroutine[Any, Any, Tuple[str, Dict[str, Score]]]] = [self.__evaluate(model, dataset, evaluation_metrics, self.__logger.getChild(str(dataset[0]))) for dataset in evaluation_datasets.items()]

        experiment_results: List[Tuple[str, Dict[str, Score]]] = await asyncio.gather(*experiment_tasks, loop=self.__event_loop)

        results = dict(experiment_results)

        self.__logger.info(f"finished evaluation on {len(evaluation_datasets)} datasets.")

        return results