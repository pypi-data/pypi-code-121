from numbers import Number
from typing import Dict, List, Optional, Tuple, Union

import cimod
import numpy as np
import openjij as oj

from jijmodeling.expression.expression import Expression

from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.post_api import post_instance_and_query
from jijzept.response import DimodResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface


class JijQIOSASampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="SA")
    jijmodeling_solver_type = SolverType(queue_name="qiosolver", solver="SAParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        platform: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Simulated Annealing solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            platform (Optional[str]): "CPU" or "FPGA". If `None`, "CPU" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOSASampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOSASampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_reads": num_reads,
            "seed": seed,
            "platform": platform,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        platform: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Simulated Annealing solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            platform (Optional[str]): "CPU" or "FPGA". If `None`, "CPU" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOSASampler(config='config.toml')
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
            num_sweeps=num_sweeps,
            beta_min=beta_min,
            beta_max=beta_max,
            num_reads=num_reads,
            seed=seed,
            platform=platform,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        platform: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO simulated annealing solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            platform (Optional[str]): "CPU" or "FPGA". If `None`, "CPU" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSASampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_reads": num_reads,
            "seed": seed,
            "platform": platform,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        platform: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO simulated annealing solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            platform (Optional[str]): "CPU" or "FPGA". If `None`, "CPU" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSASampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_reads": num_reads,
            "seed": seed,
            "platform": platform,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        platform: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO simulated annealing solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            platform (Optional[str]): "CPU" or "FPGA". If `None`, "CPU" will be set.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSASampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_reads": num_reads,
            "seed": seed,
            "platform": platform,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )


class JijQIOPASampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="PA")
    jijmodeling_solver_type = SolverType(queue_name="qiosolver", solver="PAParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        population: Optional[int] = None,
        schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Population Annealing solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            population (Optional[int], optional): The number of walkers in the population (must be positive). If `None`, this will be set automatically.
            schedule_type (Optional[str], optional): "linear" or "geometric".
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOPASampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOPASampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "population": population,
            "schedule_type": schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        population: Optional[int] = None,
        schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Population Annealing solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            population (Optional[int], optional): The number of walkers in the population (must be positive). If `None`, this will be set automatically.
            schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOPASampler(config='config.toml')
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
            num_sweeps=num_sweeps,
            beta_min=beta_min,
            beta_max=beta_max,
            population=population,
            schedule_type=schedule_type,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        population: Optional[int] = None,
        schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO population annealing solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            population (Optional[int], optional): The number of walkers in the population (must be positive). If `None`, this will be set automatically.
            schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPASampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "population": population,
            "schedule_type": schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        population: Optional[int] = None,
        schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO population annealing solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            population (Optional[int], optional): The number of walkers in the population (must be positive). If `None`, this will be set automatically.
            schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPASampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "population": population,
            "schedule_type": schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        population: Optional[int] = None,
        schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO population annealing solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            population (Optional[int], optional): The number of walkers in the population (must be positive). If `None`, this will be set automatically.
            schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPASampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "population": population,
            "schedule_type": schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )


class JijQIOPTSampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="PT")
    jijmodeling_solver_type = SolverType(queue_name="qiosolver", solver="PTParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        num_sweeps: Optional[int] = None,
        replicas: Optional[int] = None,
        all_betas: Optional[List[Union[int, float]]] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Parallel Tempering solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            replicas (Optional[int], optional): The number of concurrent running copies for sampling. Each instance will start with a random configuration.
            all_betas (Optional[List[Union[int, float]]]): The list of beta values used in each replica for sampling. The number of beta values must equal the number of replicas, as each replica will be assigned one beta value from the list.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOPTSampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOPTSampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "replicas": replicas,
            "all_betas": all_betas,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        num_sweeps: Optional[int] = None,
        replicas: Optional[int] = None,
        all_betas: Optional[List[Union[int, float]]] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Parallel Tempering solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            replicas (Optional[int], optional): The number of concurrent running copies for sampling. Each instance will start with a random configuration.
            all_betas (Optional[List[Union[int, float]]]): The list of beta values used in each replica for sampling. The number of beta values must equal the number of replicas, as each replica will be assigned one beta value from the list.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOPTSampler(config='config.toml')
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
            num_sweeps=num_sweeps,
            replicas=replicas,
            all_betas=all_betas,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        num_sweeps: Optional[int] = None,
        replicas: Optional[int] = None,
        all_betas: Optional[List[Union[int, float]]] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO parallel tempering solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            replicas (Optional[int], optional): The number of concurrent running copies for sampling. Each instance will start with a random configuration.
            all_betas (Optional[List[Union[int, float]]]): The list of beta values used in each replica for sampling. The number of beta values must equal the number of replicas, as each replica will be assigned one beta value from the list.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPTSampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "replicas": replicas,
            "all_betas": all_betas,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        num_sweeps: Optional[int] = None,
        replicas: Optional[int] = None,
        all_betas: Optional[List[Union[int, float]]] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO parallel tempering solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            replicas (Optional[int], optional): The number of concurrent running copies for sampling. Each instance will start with a random configuration.
            all_betas (Optional[List[Union[int, float]]]): The list of beta values used in each replica for sampling. The number of beta values must equal the number of replicas, as each replica will be assigned one beta value from the list.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPTSampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "replicas": replicas,
            "all_betas": all_betas,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        num_sweeps: Optional[int] = None,
        replicas: Optional[int] = None,
        all_betas: Optional[List[Union[int, float]]] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO parallel tempering solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            replicas (Optional[int], optional): The number of concurrent running copies for sampling. Each instance will start with a random configuration.
            all_betas (Optional[List[Union[int, float]]]): The list of beta values used in each replica for sampling. The number of beta values must equal the number of replicas, as each replica will be assigned one beta value from the list.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOPTSampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "replicas": replicas,
            "all_betas": all_betas,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )


class JijQIOTBSampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="TB")
    jijmodeling_solver_type = SolverType(queue_name="qiosolver", solver="TBParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        num_sweeps: Optional[int] = None,
        tabu_tenure: Optional[int] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Tabu Search solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            tabu_tenure (Optional[int], optional): Tenure of the tabu list in moves. Describes how many moves a variable stays on the tabu list once it has been made.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOTBSampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOTBSampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "tabu_tenure": tabu_tenure,
            "num_reads": num_reads,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        num_sweeps: Optional[int] = None,
        tabu_tenure: Optional[int] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Tabu Search solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            tabu_tenure (Optional[int], optional): Tenure of the tabu list in moves. Describes how many moves a variable stays on the tabu list once it has been made.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOTBSampler(config='config.toml')
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
            num_sweeps=num_sweeps,
            tabu_tenure=tabu_tenure,
            num_reads=num_reads,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        num_sweeps: Optional[int] = None,
        tabu_tenure: Optional[int] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO tabu search solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            tabu_tenure (Optional[int], optional): Tenure of the tabu list in moves. Describes how many moves a variable stays on the tabu list once it has been made.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOTBSampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "tabu_tenure": tabu_tenure,
            "num_reads": num_reads,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        num_sweeps: Optional[int] = None,
        tabu_tenure: Optional[int] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO tabu search solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            tabu_tenure (Optional[int], optional): Tenure of the tabu list in moves. Describes how many moves a variable stays on the tabu list once it has been made.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOTBSampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "tabu_tenure": tabu_tenure,
            "num_reads": num_reads,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        num_sweeps: Optional[int] = None,
        tabu_tenure: Optional[int] = None,
        num_reads: Optional[int] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO tabu search solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            tabu_tenure (Optional[int], optional): Tenure of the tabu list in moves. Describes how many moves a variable stays on the tabu list once it has been made.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOTBSampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "tabu_tenure": tabu_tenure,
            "num_reads": num_reads,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )


class JijQIOSQASampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="SQA")
    jijmodeling_solver_type = SolverType(queue_name="qiosolver", solver="SQAParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        beta: Optional[float] = None,
        trotter: Optional[int] = None,
        transverse_field_max: Optional[float] = None,
        transverse_field_min: Optional[float] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Quantum Monte Carlo solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            beta (Optional[float], optional): Temperature at which the annealing schedule is executed.
            trotter (Optional[int], optional): The number of copies of every variable to generate for running the simulation.
            transverse_field_max (Optional[float], optional): Starting value of the external field applied to the annealing schedule.
            transverse_field_min (Optional[float], optional): Stopping value of the external field applied to the annealing schedule.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOSQASampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOSQASampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "beta": beta,
            "trotter": trotter,
            "transverse_field_max": transverse_field_max,
            "transverse_field_min": transverse_field_min,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        beta: Optional[float] = None,
        trotter: Optional[int] = None,
        transverse_field_max: Optional[float] = None,
        transverse_field_min: Optional[float] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Quantum Monte Carlo solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            beta (Optional[float], optional): Temperature at which the annealing schedule is executed.
            trotter (Optional[int], optional): The number of copies of every variable to generate for running the simulation.
            transverse_field_max (Optional[float], optional): Starting value of the external field applied to the annealing schedule.
            transverse_field_min (Optional[float], optional): Stopping value of the external field applied to the annealing schedule.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOSQASampler(config='config.toml')
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
            num_sweeps=num_sweeps,
            num_reads=num_reads,
            beta=beta,
            trotter=trotter,
            transverse_field_max=transverse_field_max,
            transverse_field_min=transverse_field_min,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        beta: Optional[float] = None,
        trotter: Optional[int] = None,
        transverse_field_max: Optional[float] = None,
        transverse_field_min: Optional[float] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO quantum monte carlo solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            beta (Optional[float], optional): Temperature at which the annealing schedule is executed.
            trotter (Optional[int], optional): The number of copies of every variable to generate for running the simulation.
            transverse_field_max (Optional[float], optional): Starting value of the external field applied to the annealing schedule.
            transverse_field_min (Optional[float], optional): Stopping value of the external field applied to the annealing schedule.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSQASampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "beta": beta,
            "trotter": trotter,
            "transverse_field_max": transverse_field_max,
            "transverse_field_min": transverse_field_min,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        beta: Optional[float] = None,
        trotter: Optional[int] = None,
        transverse_field_max: Optional[float] = None,
        transverse_field_min: Optional[float] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO quantum monte carlo solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            beta (Optional[float], optional): Temperature at which the annealing schedule is executed.
            trotter (Optional[int], optional): The number of copies of every variable to generate for running the simulation.
            transverse_field_max (Optional[float], optional): Starting value of the external field applied to the annealing schedule.
            transverse_field_min (Optional[float], optional): Stopping value of the external field applied to the annealing schedule.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSQASampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "beta": beta,
            "trotter": trotter,
            "transverse_field_max": transverse_field_max,
            "transverse_field_min": transverse_field_min,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        num_sweeps: Optional[int] = None,
        num_reads: Optional[int] = None,
        beta: Optional[float] = None,
        trotter: Optional[int] = None,
        transverse_field_max: Optional[float] = None,
        transverse_field_min: Optional[float] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO quantum monte carlo solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            num_sweeps (Optional[int], optional): The number of steps. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            beta (Optional[float], optional): Temperature at which the annealing schedule is executed.
            trotter (Optional[int], optional): The number of copies of every variable to generate for running the simulation.
            transverse_field_max (Optional[float], optional): Starting value of the external field applied to the annealing schedule.
            transverse_field_min (Optional[float], optional): Stopping value of the external field applied to the annealing schedule.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSQASampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "beta": beta,
            "trotter": trotter,
            "transverse_field_max": transverse_field_max,
            "transverse_field_min": transverse_field_min,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )


class JijQIOSSMCSampler(JijModelingInterface):
    solver_type: SolverType = SolverType(queue_name="qiosolver", solver="SSMC")
    jijmodeling_solver_type = SolverType(
        queue_name="qiosolver", solver="SSMCParaSearch"
    )

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample(
        self,
        model: Union[
            cimod.BinaryQuadraticModel,
            oj.BinaryQuadraticModel,
            cimod.BinaryPolynomialModel,
            oj.BinaryPolynomialModel,
        ],
        step_limit: Optional[int] = None,
        target_population: Optional[int] = None,
        alpha_min: Optional[float] = None,
        alpha_max: Optional[float] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        alpha_schedule_type: Optional[str] = None,
        beta_schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using BinaryQuadraticModel or BinaryPolynomialModel by means of Microsoft QIO Substochastic Monte Carlo solver.

        Args:
            model (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel, cimod.BinaryPolynomialModel, openjij.BinaryPolynomialModel]): Binary quadratic model or binary polynomial model.
            step_limit (Optional[int], optional): Number of monte carlo steps.
            target_population (Optional[int], optional): The number of walkers in the population (should be greater-equal 8)
            alpha_min (Optional[float], optional): The minimum (final) stepping chance. If `None`, this will be set automatically.
            alpha_max (Optional[float], optional): The maximum (initial) stepping chance. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            alpha_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            beta_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import openjij as oj
        bqm = oj.BinaryQuadraticModel({"a": -1}, {("a", "b"):1}, "SPIN")
        bpm = oj.BinaryPolynomialModel({("a", "b", "c", "d"):1}, "BINARY")
        response_bqm = jz.JijQIOSSMCSampler(config='config.toml').sample(bqm_oj)
        response_bpm = jz.JijQIOSSMCSampler(config='config.toml').sample(bpm_oj)
        ```
        """

        parameters = {
            "step_limit": step_limit,
            "target_population": target_population,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "alpha_schedule_type": alpha_schedule_type,
            "beta_schedule_type": beta_schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=model.to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
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
        step_limit: Optional[int] = None,
        target_population: Optional[int] = None,
        alpha_min: Optional[float] = None,
        alpha_max: Optional[float] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        alpha_schedule_type: Optional[str] = None,
        beta_schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Substochastic Monte Carlo solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            step_limit (Optional[int], optional): Number of monte carlo steps.
            target_population (Optional[int], optional): The number of walkers in the population (should be greater-equal 8)
            alpha_min (Optional[float], optional): The minimum (final) stepping chance. If `None`, this will be set automatically.
            alpha_max (Optional[float], optional): The maximum (initial) stepping chance. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            alpha_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            beta_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

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
        sampler = jz.JijQIOSSMCSampler(config='config.toml')
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
            step_limit=step_limit,
            target_population=target_population,
            alpha_min=alpha_min,
            alpha_max=alpha_max,
            beta_min=beta_min,
            beta_max=beta_max,
            alpha_schedule_type=alpha_schedule_type,
            beta_schedule_type=beta_schedule_type,
            seed=seed,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

    def sample_ising(
        self,
        h: Dict,
        J: Dict,
        step_limit: Optional[int] = None,
        target_population: Optional[int] = None,
        alpha_min: Optional[float] = None,
        alpha_max: Optional[float] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        alpha_schedule_type: Optional[str] = None,
        beta_schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO substochastic monte carlo solver is performed for Ising models.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            step_limit (Optional[int], optional): Number of monte carlo steps.
            target_population (Optional[int], optional): The number of walkers in the population (should be greater-equal 8)
            alpha_min (Optional[float], optional): The minimum (final) stepping chance. If `None`, this will be set automatically.
            alpha_max (Optional[float], optional): The maximum (initial) stepping chance. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            alpha_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            beta_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSSMCSampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},)
        ```
        """

        parameters = {
            "step_limit": step_limit,
            "target_population": target_population,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "alpha_schedule_type": alpha_schedule_type,
            "beta_schedule_type": beta_schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryQuadraticModel(h, J, "SPIN").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_qubo(
        self,
        Q: Dict,
        step_limit: Optional[int] = None,
        target_population: Optional[int] = None,
        alpha_min: Optional[float] = None,
        alpha_max: Optional[float] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        alpha_schedule_type: Optional[str] = None,
        beta_schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO substochastic monte carlo solver is performed for binary quadratic models.

        Args:
            Q (Dict): The linear or quadratic terms.
            step_limit (Optional[int], optional): Number of monte carlo steps.
            target_population (Optional[int], optional): The number of walkers in the population (should be greater-equal 8)
            alpha_min (Optional[float], optional): The minimum (final) stepping chance. If `None`, this will be set automatically.
            alpha_max (Optional[float], optional): The maximum (initial) stepping chance. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            alpha_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            beta_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSSMCSampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1})
        ```
        """

        parameters = {
            "step_limit": step_limit,
            "target_population": target_population,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "alpha_schedule_type": alpha_schedule_type,
            "beta_schedule_type": beta_schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(Q, "BINARY").to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

    def sample_hubo(
        self,
        J: Dict,
        vartype: str,
        step_limit: Optional[int] = None,
        target_population: Optional[int] = None,
        alpha_min: Optional[float] = None,
        alpha_max: Optional[float] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        alpha_schedule_type: Optional[str] = None,
        beta_schedule_type: Optional[str] = None,
        seed: Optional[int] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Microsoft QIO substochastic monte carlo solver is performed for binary polynomial models.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            step_limit (Optional[int], optional): Number of monte carlo steps.
            target_population (Optional[int], optional): The number of walkers in the population (should be greater-equal 8)
            alpha_min (Optional[float], optional): The minimum (final) stepping chance. If `None`, this will be set automatically.
            alpha_max (Optional[float], optional): The maximum (initial) stepping chance. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            alpha_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            beta_schedule_type (Optional[str], optional): "linear" or "geometric". If `None`, "linear" will be set.
            seed (Optional[int], optional): Seed for reproducing results. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijQIOSSMCSampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN")
        ```
        """

        parameters = {
            "step_limit": step_limit,
            "target_population": target_population,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "alpha_schedule_type": alpha_schedule_type,
            "beta_schedule_type": beta_schedule_type,
            "seed": seed,
        }

        return post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BPM",
            instance=oj.BinaryPolynomialModel(J, vartype).to_serializable(),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )
