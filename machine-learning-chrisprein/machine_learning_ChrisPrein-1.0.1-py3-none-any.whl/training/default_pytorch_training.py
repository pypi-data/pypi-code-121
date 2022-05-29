from logging import Logger
from typing import List, Tuple
from torch.utils.data import Dataset, random_split

from ..modeling.pytorch_model import PytorchModel
from .abstractions.stop_condition import TrainingContext
from ..evaluation.abstractions.evaluation_metric import EvaluationContext, TModel
from ..modeling.abstractions.model import Model, TInput, TTarget

def pytorch_pre_loop(logger: Logger, training_context: TrainingContext[TInput, TTarget, PytorchModel[TInput, TTarget]]):
    model: PytorchModel[TInput, TTarget] = training_context.model

    if not model.optimizer_factory is None:
        model.optimizer = model.optimizer_factory()

    if not model.scheduler_factory is None:
        model.scheduler = model.scheduler_factory()

def pytorch_post_epoch(logger: Logger, training_context: TrainingContext[TInput, TTarget, PytorchModel[TInput, TTarget]], validation_dataset: Dataset[Tuple[TInput, TTarget]]):
    model: PytorchModel[TInput, TTarget] = training_context.model

    if not model.scheduler is None:
        model.scheduler.step()