from numbers import Number
from typing import Dict, List, Optional, Tuple, Union

import cimod
import numpy as np
import openjij

from jijmodeling.expression.expression import Expression

from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.post_api import post_instance_and_query
from jijzept.response import APIStatus, DimodResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface


class JijSwapMovingSampler(JijModelingInterface):

    solver_type: SolverType = SolverType(queue_name="swapmovingsolver", solver="SA")
    jijmodeling_solver_type = SolverType(
        queue_name="swapmovingsolver", solver="SAParaSearch"
    )

    def __init__(
        self,
        token: str = None,
        url: Union[str, dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def get_result(self, solution_id: str):
        response = DimodResponse.empty_response(
            APIStatus.PENDING, self.client, solution_id
        )

        return response.get_result()

    @property
    def properties(self):
        return dict()

    @property
    def parameters(self):
        return dict()

    def _select_index_type_from_interactions(self, J: Optional[dict] = None):
        if J is None:
            return "IndexType.INT"
        elif isinstance(J, dict):
            if len(J) == 0:
                return "IndexType.INT"
            else:
                for key in J.keys():
                    if not isinstance(key, tuple):
                        raise TypeError("Invalid Interactions")
                    else:
                        for i in range(len(key)):
                            if isinstance(key[i], int):
                                return "IndexType.INT"
                            elif isinstance(key[i], str):
                                return "IndexType.STRING"
                            elif isinstance(key[i], tuple):
                                if len(key[i]) == 2:
                                    return "IndexType.INT_TUPLE_2"
                                elif len(key[i]) == 3:
                                    return "IndexType.INT_TUPLE_3"
                                elif len(key[i]) == 4:
                                    return "IndexType.INT_TUPLE_4"
                        raise TypeError("Invalid Interactions")
        else:
            raise TypeError("Invalid Interactions")

    def _select_index_type_from_linear(self, h: Optional[dict] = None):
        if h is None:
            return "IndexType.INT"
        elif isinstance(h, dict):
            if len(h) == 0:
                return "IndexType.INT"
            else:
                for key in h.keys():
                    if isinstance(key, int):
                        return "IndexType.INT"
                    elif isinstance(key, str):
                        return "IndexType.STRING"
                    elif isinstance(key, tuple) and len(key) == 2:
                        return "IndexType.INT_TUPLE_2"
                    elif isinstance(key, tuple) and len(key) == 3:
                        return "IndexType.INT_TUPLE_3"
                    elif isinstance(key, tuple) and len(key) == 4:
                        return "IndexType.INT_TUPLE_4"
                    raise TypeError("Invalid linear terms")
        else:
            raise TypeError("Invalid linear terms")

    def _to_serializable(
        self, offset, linear, interaction, penalties, constraints, vartype
    ):
        if len(linear) != 0:
            index_type = self._select_index_type_from_linear(linear)
        elif len(interaction) != 0:
            index_type = self._select_index_type_from_interactions(interaction)
        else:
            raise TypeError("Interactions are empty")

        if vartype == openjij.SPIN:
            vartype = "SPIN"
        elif vartype == openjij.BINARY:
            vartype = "BINARY"

        if constraints is None:
            constraints = []

        p_lambda = []
        p_key = []
        p_value = []
        p_constant = []

        if penalties is not None:
            for p in penalties:
                p_lambda.append(p[0])
                p_key.append(list(p[1].keys()))
                p_value.append(list(p[1].values()))
                p_constant.append(p[2])

        return {
            "data_format_type": "openjij.BinaryQuadraticModel",
            "model_type": "jijpro.BinaryModel",
            "index_type": index_type,
            "vartype": vartype,
            "offset": offset,
            "linear_key": list(linear.keys()),
            "linear_value": list(linear.values()),
            "interaction_key": list(interaction.keys()),
            "interaction_value": list(interaction.values()),
            "constraints": constraints,
            "penalties_lambda": p_lambda,
            "penalties_key": p_key,
            "penalties_value": p_value,
            "penalties_constant": p_constant,
        }

    def sample(
        self,
        bqm: Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel],
        constraints: Optional[List] = None,
        penalties: Optional[List] = None,
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
        """The simulated annealing is performed for BinaryQuadraticModel with the linear constraint conditions.
        Note here that the linear constraint conditions are strictly satisfied.

        Args:
            bqm (Union[cimod.BinaryQuadraticModel, openjij.BinaryQuadraticModel]): Binary quadratic model.
            constraints (Optional[List[List, int]]): The list of constraint conditions which can be represented as linear equations.
            penalties (Optional[List[float, List, int]]): The list of penarty terms which can be represented as linear equations.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm must be "swap moving" for now. If `None`, "swap moving" will be set.
            sparse (Optional[bool], optional): If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `True` will be set.
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
        bqm = cimod.BinaryQuadraticModel({0: -1, 2: -1}, {(0, 1): -1, (1, 3): -1}, "SPIN")
        sampler = jz.JijSwapMovingSampler(config='config.toml')
        response = sampler.sample(bqm, constraints=[([0,1], 0), ([2,3], 0)])
        ```

        """

        parameters = {
            "constraints": constraints,
            "penalties": penalties,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "initial_state": initial_state,
            "updater": updater,
            "sparse": sparse,
            "reinitialize_state": reinitialize_state,
            "seed": seed,
        }

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BQM",
            instance=self._to_serializable(
                bqm.get_offset(),
                bqm.get_linear(),
                bqm.get_quadratic(),
                penalties,
                constraints,
                bqm.vartype,
            ),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )
        return response

    def sample_ising(
        self,
        h: dict,
        J: dict,
        constraints: Optional[List] = None,
        penalties: Optional[List] = None,
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
        """The simulated annealing is performed for Ising models with the linear constraint conditions.
        Note here that the linear constraint conditions are strictly satisfied.

        Args:
            h (Dict): The linear terms.
            J (Dict): The quadratic terms.
            constraints (Optional[List[List, int]]): The list of constraint conditions which can be represented as linear equations.
            penalties (Optional[List[float, List, int]]): The list of penarty terms which can be represented as linear equations.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm must be "swap moving" for now. If `None`, "swap moving" will be set.
            sparse (Optional[bool], optional): If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `True` will be set.
            reinitialize_state (Optional[bool], optional): If `True`, reinitialize state for each run. If `None`, `True` will be set.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijSwapMovingSampler(config='config.toml')
        response = sampler.sample_ising(h={0: +0.5, 2: -0.5},
                                        J={(0,1):-1, (0,3):-1},
                                        constraints=[([0,1], 0), ([2,3], 0)])
        ```

        """

        parameters = {
            "constraints": constraints,
            "penalties": penalties,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "initial_state": initial_state,
            "updater": updater,
            "sparse": sparse,
            "reinitialize_state": reinitialize_state,
            "seed": seed,
        }

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BQM",
            instance=self._to_serializable(0.0, h, J, penalties, constraints, "SPIN"),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

        return response

    def sample_qubo(
        self,
        Q: dict,
        constraints: Optional[List] = None,
        penalties: Optional[List] = None,
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
        """The simulated annealing is performed for binary quadratic models with the linear constraint conditions.
        Note here that the linear constraint conditions are strictly satisfied.

        Args:
            Q (Dict): The linear or quadratic terms.
            constraints (Optional[List[List, int]]): The list of constraint conditions which can be represented as linear equations.
            penalties (Optional[List[float, List, int]]): The list of penarty terms which can be represented as linear equations.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm must be "swap moving" for now. If `None`, "swap moving" will be set.
            sparse (Optional[bool], optional): If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `True` will be set.
            reinitialize_state (Optional[bool], optional): If `True`, reinitialize state for each run. If `None`, `True` will be set.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijSwapMovingSampler(config='config.toml')
        response = sampler.sample_qubo(Q={(0,0): -0.5, (0,1): -1, (0,2): -1, (2,3): -1},
                                       constraints=[([0,1], 1), ([2,3], 1)])
        ```

        """

        parameters = {
            "constraints": constraints,
            "penalties": penalties,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "initial_state": initial_state,
            "updater": updater,
            "sparse": sparse,
            "reinitialize_state": reinitialize_state,
            "seed": seed,
        }

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BQM",
            instance=self._to_serializable(
                0.0, {}, Q, penalties, constraints, "BINARY"
            ),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

        return response

    def sample_hubo(
        self,
        J: dict,
        vartype: str,
        constraints: Optional[List] = None,
        penalties: Optional[List] = None,
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
        """The simulated annealing is performed for higher ordered unconstraind binary optimizations (hubo) with the linear constraint conditions.
        Note here that the linear constraint conditions are strictly satisfied.

        Args:
            J (Dict): Polynomial interactions.
            vartype (str): The variable type. "SPIN" or "BINARY".
            constraints (Optional[List[List, int]]): The list of constraint conditions which can be represented as linear equations.
            penalties (Optional[List[float, List, int]]): The list of penarty terms which can be represented as linear equations.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, 1000 will be set.
            num_reads (Optional[int], optional): The number of samples. If `None`, 1 will be set.
            initial_state (Optional[dict], optional): Initial state. If `None`, this will be set automatically.
            updater (Optional[str], optional): Updater algorithm must be "swap moving" for now. If `None`, "swap moving" will be set.
            sparse (Optional[bool], optional): Must be `True` for now. If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `True` will be set.
            reinitialize_state (Optional[bool], optional): If `True`, reinitialize state for each run. If `None`, `True` will be set.
            seed (Optional[int], optional): Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.
            queue_name (str, optional): queue_name.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        sampler = jz.JijSwapMovingSampler(config='config.toml')
        response = sampler.sample_hubo(J={(0,1,2,3,4): -1}, vartype="SPIN",
                                       constraints=[([0,1], 0), ([2,3,4], 1)])
        ```

        """

        parameters = {
            "constraints": constraints,
            "penalties": penalties,
            "beta_min": beta_min,
            "beta_max": beta_max,
            "num_sweeps": num_sweeps,
            "num_reads": num_reads,
            "initial_state": initial_state,
            "updater": updater,
            "sparse": sparse,
            "reinitialize_state": reinitialize_state,
            "seed": seed,
        }

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type="BQM",
            instance=self._to_serializable(0.0, {}, J, penalties, constraints, vartype),
            queue_name=self.solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )

        return response

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
            updater (Optional[str], optional): Updater algorithm must be "swap moving" for now. If `None`, "swap moving" will be set.
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
        problem += jm.Constraint("one-hot", jm.Sum(i, x[i]) == 1)
        sampler = jz.JijSwapMovingSampler(config='config.toml')
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
