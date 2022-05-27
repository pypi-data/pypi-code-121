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


class JijSASampler(JijZeptSampler, JijModelingInterface):

    solver_type = SolverType(queue_name="openjijsolver", solver="SA")
    hubo_solver_type = SolverType(queue_name="openjijsolver", solver="HUBOSA")
    jijmodeling_solver_type = SolverType(
        queue_name="openjijsolver", solver="SAParaSearch"
    )

    def sample(
        self,
        bqm: Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel],
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        initial_state: Optional[Union[list, dict]] = None,
        updater: Optional[str] = None,
        sparse: Optional[bool] = None,
        reinitialize_state: Optional[bool] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel by means of the simulated annealing.

        Args:
            bqm (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel]): Binary quadratic model.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm. "single spin flip" or "swendsen wang". If `None`, "single spin flip" will be set.
            sparse (Optional[bool], optional): If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `False` will be set.
            reinitialize_state (Optional[bool], optional): If `True`, reinitialize state for each run. If `None`, `True` will be set.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        For `cimod.BinaryQuadraticModel` case:

        ```python
        import jijzept as jz
        import cimod
        bqm = cimod.BinaryQuadraticModel({0: -1, 1: -1}, {(0, 1): -1, (1, 2): -1}, "SPIN")
        sampler = jz.JijSASampler(config='config.toml')
        response = sampler.sample(bqm)
        ```

        One can also use `sample_ising` and `sample_qubo` methods.

        For Ising case:

        ```python
        import jijzept as jz
        h = {0: -1, 1: -1, 2: 1, 3: 1}
        J = {(0, 1): -1, (3, 4): -1}
        sampler = jz.JijSASampler(config='config.toml')
        response = sampler.sample_ising(h, J)
        ```

        For QUBO case:

        ```python
        import jijzept as jz
        Q = {(0, 0): -1, (1, 1): -1, (2, 2): 1, (0, 1): -1, (1, 2): 1}
        sampler = jz.JijSASampler(config='config.toml')
        response = sampler.sample_qubo(Q)
        ```
        """

        return super().sample(
            bqm,
            beta_min=beta_min,
            beta_max=beta_max,
            num_sweeps=num_sweeps,
            num_reads=num_reads,
            initial_state=initial_state,
            updater=updater,
            sparse=sparse,
            reinitialize_state=reinitialize_state,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_hubo(
        self,
        J: dict,
        vartype: str,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        initial_state: Optional[Union[list, dict]] = None,
        updater: Optional[str] = None,
        reinitialize_state: Optional[bool] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryPolynomialModel by means of the simulated annealing.

        Args:
            J (dict): Polynomial interactions.
            vartype (str): Variable type. "SPIN" or "BINARY".
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm. "single spin flip" or "k-local". If `None`, "single spin flip" will be set. One can select "k-local" only for `vartype`="BINARY".
            reinitialize_state (Optional[bool], optional): If `True`, reinitialize state for each run. If `None`, `True` will be set.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        For spin variable case:

        ```python
        import jijzept as jz
        sampler = jz.JijSASampler(config='config.toml')
        J = {(0,): -1, (0, 1): -1, (0, 1, 2): 1}
        response = sampler.sample_hubo(J, "SPIN")
        ```

        For binary variable case:

        ```python
        import jijzept as jz
        sampler = jz.JijSASampler(config='config.toml')
        J = {(0,): -1, (0, 1): -1, (0, 1, 2): 1}
        response = sampler.sample_hubo(J, "BINARY")
        ```

        """

        return super().sample_hubo(
            J,
            vartype=vartype,
            beta_min=beta_min,
            beta_max=beta_max,
            num_sweeps=num_sweeps,
            num_reads=num_reads,
            initial_state=initial_state,
            updater=updater,
            reinitialize_state=reinitialize_state,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
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
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        updater: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of the simulated annealing.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            updater (Optional[str], optional): Updater algorithm. "single spin flip" or "swendsen wang". If `None`, "single spin flip" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
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
        sampler = jz.JijSASampler(config='config.toml')
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
            beta_min=beta_min,
            beta_max=beta_max,
            num_sweeps=num_sweeps,
            num_reads=num_reads,
            updater=updater,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )
