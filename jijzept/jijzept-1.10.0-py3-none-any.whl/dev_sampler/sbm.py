from numbers import Number
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from jijmodeling.expression.expression import Expression

from jijzept.entity.schema import SolverType
from jijzept.sampler.jijmodel_post import JijModelingInterface
from jijzept.sampler.sampler import JijZeptSampler


class JijSBMSampler(JijZeptSampler, JijModelingInterface):
    solver_type = SolverType(queue_name="sbmsolver", solver="SBM")
    jijmodeling_solver_type = SolverType(queue_name="sbmsolver", solver="SBMParaSearch")

    def sample(
        self,
        bqm,
        steps=None,
        loops=None,
        maxwait=None,
        target=None,
        prefer="auto",
        stats="none",
        dt=None,
        C=None,
        timeout=None,
        sync=True,
        queue_name: Optional[str] = None,
    ) -> Any:
        """Samples by SBM.

        Args:
            bqm (:obj:`dimod.BinaryQuadraticModel`): Binary quadratic model.
            steps (int, optional): The number of steps in SBM calculation. If `steps` is set to `0`, then the number of steps is set automatically. Defaults to 0.
            loops (int, optional): The number of loops in SBM calculation. If `loops` is set to `0`, then calculation will be repeated to the maximum calculation time. Defaults to 1.
            maxwait (int, optional): The maximum waiting time in seconds. Defaults to None.
            target (float, optional): The end condition of calculation. Defaults to None.
            prefer (str, optional): Select `'speed'` or `'auto'`. Defaults to 'auto'.
            stats (str, optional): Select `'none'`, `'summary'`, or `'full`. Defaults to 'none'.
            dt (float, optional): Time step width. Defaults to 0.1.
            C (float, optional): Positive constant coefficient. If `0` is set to `C`, then the value of `C` is set automatically. Defaults to 0.
            timeout (float, optional): The maximum calculation time in seconds. Defaults to None.
            sync (bool, optional): Synchronization mode. Defaults to True.
            queue_name (str, optional): queue_name.

        Returns:
            :obj:`dimod.SampleSet`: Stores minimum energy sample.

        """
        return super().sample(
            bqm,
            steps=steps,
            loops=loops,
            maxwait=maxwait,
            target=target,
            prefer=prefer,
            stats=stats,
            dt=dt,
            C=C,
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
        steps=None,
        loops=None,
        maxwait=None,
        target=None,
        prefer="auto",
        stats="none",
        dt=None,
        C=None,
        timeout: Optional[float] = None,
        sync=True,
        queue_name: Optional[str] = None,
    ):
        """sample_model.

        Args:
            model (Expression): model
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): feed_dict
            multipliers (Dict[str, Number]): multipliers
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool): search
            steps (int, optional): The number of steps in SBM calculation. If `steps` is set to `0`, then the number of steps is set automatically. Defaults to 0.
            loops (int, optional): The number of loops in SBM calculation. If `loops` is set to `0`, then calculation will be repeated to the maximum calculation time. Defaults to 1.
            maxwait (int, optional): The maximum waiting time in seconds. Defaults to None.
            target (float, optional): The end condition of calculation. Defaults to None.
            prefer (str, optional): Select `'speed'` or `'auto'`. Defaults to 'auto'.
            stats (str, optional): Select `'none'`, `'summary'`, or `'full`. Defaults to 'none'.
            dt (float, optional): Time step width. Defaults to 0.1.
            C (float, optional): Positive constant coefficient. If `0` is set to `C`, then the value of `C` is set automatically. Defaults to 0.
            timeout (float, optional): The maximum calculation time in seconds. Defaults to None.
            sync (bool, optional): Synchronization mode. Defaults to True.
            queue_name (str, optional): queue_name.
        """

        return super().sample_model(
            model,
            feed_dict=feed_dict,
            multipliers=multipliers,
            fixed_variables=fixed_variables,
            search=search,
            num_search=num_search,
            steps=steps,
            loops=loops,
            maxwait=maxwait,
            target=target,
            prefer=prefer,
            stats=stats,
            dt=dt,
            C=C,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )
