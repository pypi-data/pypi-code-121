from numbers import Number
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from jijmodeling.expression.expression import Expression

from jijzept.entity.schema import SolverType
from jijzept.response import DimodResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface
from jijzept.sampler.sampler import JijZeptSampler


class JijDWaveLeapSampler(JijZeptSampler, JijModelingInterface):
    solver_type = SolverType(queue_name="dwaveleapsolver", solver="DWave")
    jijmodeling_solver_type = SolverType(
        queue_name="dwaveleapsolver", solver="DWaveParaSearch"
    )

    def sample(
        self,
        bqm,
        num_reads: Optional[int] = None,
        annealing_time: Optional[float] = None,
        auto_scale: Optional[bool] = None,
        annealing_schedule: Optional[List[List[float]]] = None,
        timeout: Optional[float] = None,
        sync=True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Samples by D-Wave Sampler

        Args:
            bqm (dimod.BinaryQuadraticModel): Binary quadratic model.
            num_reads (Optional[int], optional): number of annealing sample. Defaults to 1.
            annealing_time (Optional[float], optional): quantum annealing time [μs]. Defaults to None.
            auto_scale (Optional[bool], optional): auto scale strength of interaction. Defaults to False.
            timeout (Optional[float], optional): timeout
            sync (bool): set sync mode. Defaults to True.
            queue_name (str, optional): queue_name.

        Returns:
            :obj:`dimod.SampleSet`: Stores minimum energy samples.
        """

        return super().sample(
            bqm,
            num_reads=num_reads,
            annealing_time=annealing_time,
            auto_scale=auto_scale,
            annealing_schedule=annealing_schedule,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_model(
        self,
        model: Expression,
        feed_dict: Dict[str, Union[Number, list, np.ndarray]] = {},
        multipliers: Dict[str, Number] = {},
        fixed_variables: Dict[str, Dict[Tuple[int, ...], Union[int, float]]] = {},
        search: bool = False,
        num_search: int = 15,
        algorithm: Optional[str] = None,
        num_reads: Optional[int] = None,
        annealing_time: Optional[float] = None,
        auto_scale: Optional[bool] = None,
        annealing_schedule: Optional[List[List[float]]] = None,
        timeout: Optional[float] = None,
        sync=True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """sample using jijmodeling

        Args:
            model (Expression): model
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): feed_dict
            multipliers (Dict[str, Number]): multipliers
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool): search
            num_search (int): num_search
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_reads (Optional[int]): num_reads
            annealing_time (Optional[float]): annealing_time
            auto_scale (Optional[bool]): auto_scale
            annealing_schedule (Optional[List[List[float]]]): annealing_schedule
            timeout (Optional[float]): timeout
            sync (bool): synchronous mode
            queue_name (str, optional): queue_name.

        Returns:
            DimodResponse:
        """

        return super().sample_model(
            model,
            feed_dict=feed_dict,
            multipliers=multipliers,
            fixed_variables=fixed_variables,
            search=search,
            num_search=num_search,
            algorithm=algorithm,
            num_reads=num_reads,
            annealing_time=annealing_time,
            auto_scale=auto_scale,
            annealing_schedule=annealing_schedule,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )
