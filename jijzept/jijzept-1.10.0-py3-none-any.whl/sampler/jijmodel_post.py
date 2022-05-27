import json

from abc import ABCMeta
from numbers import Number
from typing import Dict, Optional, Tuple, TypeVar, Union

import numpy as np

from jijmodeling import Problem
from jijmodeling.expression.serializable import to_serializable
from jijmodeling.utils import serialize_fixed_var

from jijzept.entity.schema import SolverType
from jijzept.post_api import post_instance_and_query
from jijzept.response import BaseResponse, DimodResponse

ResponseType = TypeVar("ResponseType", bound=BaseResponse)


class JijModelingInterface(metaclass=ABCMeta):
    jijmodeling_solver_type: SolverType

    def sample_model(
        self,
        model: Problem,
        feed_dict: Dict[str, Union[Number, list, np.ndarray]],
        multipliers: Dict[str, Union[float, Number]],
        fixed_variables: Dict[str, Dict[Tuple[int, ...], Union[int, float]]] = {},
        search: bool = False,
        num_search: int = 15,
        algorithm: Optional[str] = None,
        timeout=None,
        sync=True,
        queue_name: Optional[str] = None,
        **kwargs,
    ):
        """abstract sample_model.

        Args:
            model (Problem): model
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): feed_dict
            multipliers (Dict[str, Union[float, Number]]): multipliers
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): fixed_variables
            search (bool): if True parameter search is enabled.
            num_search (int): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.
            kwargs:
        """

        m_seri = to_serializable(model)

        parameters = kwargs
        parameters["multipliers"] = multipliers
        parameters["mul_search"] = search
        # fixed variables must be serialized
        parameters["fixed_variables"] = serialize_fixed_var(fixed_variables)
        parameters["num_search"] = num_search
        parameters["algorithm"] = algorithm

        # convert nd.array to list
        _feed_dict = {
            k: v.tolist() if isinstance(v, np.ndarray) else v
            for k, v in feed_dict.items()
        }

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="JijModeling",
            instance={
                "mathematical_model": json.dumps(m_seri),
                "instance_data": _feed_dict,
            },
            queue_name=self.jijmodeling_solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.jijmodeling_solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

        return response
