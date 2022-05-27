from numbers import Number
from typing import Dict, Optional, Tuple, Union

import cimod
import numpy as np
import openjij

from jijmodeling.expression.expression import Expression

from jijzept.entity.schema import SolverType
from jijzept.response import DimodResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface
from jijzept.sampler.sampler import JijZeptSampler


class JijAmazonBraketDWaveSampler(JijZeptSampler, JijModelingInterface):

    solver_type = SolverType(queue_name="amazonbraket_dwavesolver", solver="DWave")
    jijmodeling_solver_type = SolverType(
        queue_name="amazonbraket_dwavesolver", solver="DWaveParaSearch"
    )

    def sample(
        self,
        bqm: Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel],
        num_reads: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """sample using D-Wave via Amazon Braket.

        Args:
            bqm (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel]): Binary quadratic model.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1000 will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronization mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:
        One can use like `JijSASampler()` as follows.

        For `cimod.BinaryQuadraticModel` case:

        ```python
        import jijzept as jz
        import cimod
        bqm = cimod.BinaryQuadraticModel({0: -1, 1: -1}, {(0, 1): -1, (1, 2): -1}, "SPIN")
        sampler = jz.JijAmazonBraketDWaveSampler(config='config.toml')
        response = sampler.sample(bqm)
        ```

        One can also use `sample_ising` and `sample_qubo` methods.

        For Ising case:

        ```python
        import jijzept as jz
        h = {0: -1, 1: -1, 2: 1, 3: 1}
        J = {(0, 1): -1, (3, 4): -1}
        sampler = jz.JijAmazonBraketDWaveSampler(config='config.toml')
        response = sampler.sample_ising(h, J)
        ```

        For QUBO case:

        ```python
        import jijzept as jz
        Q = {(0, 0): -1, (1, 1): -1, (2, 2): 1, (0, 1): -1, (1, 2): 1}
        sampler = jz.JijAmazonBraketDWaveSampler(config='config.toml')
        response = sampler.sample_qubo(Q)
        ```

        """

        return super().sample(
            bqm, num_reads=num_reads, timeout=timeout, sync=sync, queue_name=queue_name
        )

    def sample_model(
        self,
        model: Expression,
        feed_dict: Dict[str, Union[Number, list, np.ndarray]],
        multipliers: Dict[str, Number] = {},
        fixed_variables: Dict[str, Dict[Tuple[int, ...], Union[int, float]]] = {},
        search: bool = False,
        num_search: int = 15,
        algorithm: Optional[str] = None,
        num_reads: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using D-Wave via Amazon Braket.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1000 will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronization mode.
            queue_name (str, optional): queue_name.
        Returns:
           dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import jijmodeling as jm
        n = jm.Placeholder('n')
        x = jm.Binary('x', shape=n)
        d = jm.Placeholder('d', shape=n)
        i = jm.Element("i", n)
        problem = jm.Problem('problem')
        problem += jm.Sum({i: n}, d[i] * x[i])
        sampler = jz.JijAmazonBraketDWaveSampler(config='config.toml')
        response = sampler.sample_model(problem, feed_dict={'n': 5, 'd': [1,2,3,4,5]})
        ```

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
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_hubo(self, *args, **kwargs):
        """
        This function cannot be used from JijAmazonBraketDWaveSampler.
        """
        raise RuntimeError(
            f"sample_hubo cannot be called from {self.__class__.__name__}"
        )
