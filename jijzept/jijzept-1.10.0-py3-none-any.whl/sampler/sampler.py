from typing import Any, TypeVar, Union

import openjij

from cimod import BinaryPolynomialModel

from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.post_api import post_instance_and_query
from jijzept.response import APIStatus, BaseResponse, DimodResponse

ResponseType = TypeVar("ResponseType", bound=BaseResponse)


# We use openjij.sampler.BaseSampler for Ising and QUBO conversion performance.
class JijZeptSampler(openjij.sampler.BaseSampler):
    """JijZeptSampler

    another Sampler is based on this class

    """

    solver_type: SolverType
    hubo_solver_type: SolverType

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

    def sample(self, bqm, timeout=None, sync=True, queue_name=None, **kwargs) -> Any:
        """abstract sample function

        Args:
            bqm:
            timeout:
            sync:
            queue_name:
            kwargs:

        Returns:
            Any:
        """
        parameters = kwargs

        instance_type = "BQM"
        instance = bqm.to_serializable()

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type=instance_type,
            instance=instance,
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
        self, polynomial, vartype, timeout=None, sync=True, queue_name=None, **kwargs
    ) -> Any:
        """abstract sample_hubo.

        Args:
            polynomial:
            vartype:
            timeout:
            sync:
            queue_name:
            kwargs:

        Returns:
            Any:
        """
        parameters = kwargs

        instance_type = "BPM"
        instance = BinaryPolynomialModel(polynomial, vartype=vartype).to_serializable()

        response = post_instance_and_query(
            DimodResponse,
            self.client,
            instance_type=instance_type,
            instance=instance,
            queue_name=self.hubo_solver_type.queue_name
            if queue_name is None
            else queue_name,
            solver=self.hubo_solver_type.solver,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
        )
        return response

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
