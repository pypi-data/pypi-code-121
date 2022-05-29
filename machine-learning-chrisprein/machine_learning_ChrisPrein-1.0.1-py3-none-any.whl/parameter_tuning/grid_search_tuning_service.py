from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Union
from numpy import ndarray
from sklearn.model_selection import GridSearchCV
from torch.utils.data.dataset import Dataset
from sklearn import metrics

from ..modeling.adapter.sklearn_estimator_adapter import SkleanEstimatorAdapter
from .abstractions.model_factory import ModelFactory
from .abstractions.objective_function import ObjectiveFunction, OptimizationType
from ..modeling.abstractions.model import TInput, TTarget, Model
from ..evaluation.abstractions.evaluation_metric import Prediction, TModel, EvaluationContext
from .abstractions.parameter_tuning_service import ParameterTuningService

def score_function(estimator: SkleanEstimatorAdapter[Model[TInput, TTarget]], y_target: ndarray, y_predicted: ndarray, objective_function: ObjectiveFunction[TInput, TTarget, Model[TInput, TTarget]]) -> float:
    
    predictions: List[Prediction] = [Prediction(input=None, prediction=predicted, target=target) for target, predicted in zip(y_target, y_predicted)]
    context: EvaluationContext[TInput, TTarget, Model[TInput, TTarget]] = EvaluationContext[TInput, TTarget, Model[TInput, TTarget]](model=None, predictions=predictions)

    return objective_function.calculate_score(context=context)

class GridSearchTuningService(ParameterTuningService[TInput, TTarget, Model[TInput, TTarget]]):
    def __init__(self, folds: int = 5):
        self.__folds: int = folds

    async def search(self, model_factory: ModelFactory[TModel], params: Dict[str, List[Any]], dataset: Dataset[Tuple[TInput, TTarget]], objective_functions: Dict[str, ObjectiveFunction[TInput, TTarget, Model[TInput, TTarget]]], primary_objective: str) -> Dict[str, Any]:
        if model_factory is None:
            raise ValueError("model_factory can't be empty")

        if params is None:
            raise ValueError("params can't be empty")

        if dataset is None:
            raise ValueError("dataset can't be empty")

        if objective_functions is None:
            raise ValueError("objective_functions can't be empty")

        factory_params: Dict[str, Any] = {key: values[0] for key, values in params.items()}
        model: TModel = model_factory.create(factory_params)
        estimator = SkleanEstimatorAdapter[Model[TInput, TTarget]](model)
        scorer = {key: metrics.make_scorer(lambda y, y_pred, **kwargs: score_function(model, y, y_pred, objective_function), greater_is_better=objective_function.optimization_type == OptimizationType.MAX) for key, objective_function in objective_functions.items()}

        inputs: List[TInput] = [value[0] for value in dataset]
        targets: List[TTarget] = [value[1] for value in dataset]

        grid_search = GridSearchCV(estimator=estimator, param_grid=params, cv=self.__folds, scoring=scorer, refit=primary_objective)
        grid_search.fit(X=inputs, y=targets)

        return grid_search.best_params_

