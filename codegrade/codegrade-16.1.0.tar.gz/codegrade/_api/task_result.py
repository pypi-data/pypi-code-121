"""The endpoints for task_result objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.job import Job
    from ..models.result_data_get_task_result_get_all import (
        ResultDataGetTaskResultGetAll,
    )


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class TaskResultService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self: "TaskResultService[codegrade.client.AuthenticatedClient]",
        *,
        offset: "int" = 0,
        limit: "int" = 50,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ResultDataGetTaskResultGetAll":
        """Get all active tasks, all tasks that have not yet been started, a
        page of finished tasks, and the total number of finished tasks.

        :param offset: First finished task to get.
        :param limit: Amount of finished tasks to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested tasks, with the given limits applied to the
                  finished jobs.
        """

        url = "/api/v1/tasks/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "offset": utils.to_dict(offset),
            "limit": utils.to_dict(limit),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.result_data_get_task_result_get_all import (
                ResultDataGetTaskResultGetAll,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ResultDataGetTaskResultGetAll)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def get(
        self: "TaskResultService[codegrade.client.AuthenticatedClient]",
        *,
        task_result_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Job":
        """Get the state of a task result.

        To check if the task failed you should use the `state` attribute of the
        returned object as the status code of the response will still be 200.
        It is 200 as we successfully fulfilled the request, which was getting
        the task result.

        :param task_result_id: The task result to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The retrieved task result.
        """

        url = "/api/v1/task_results/{taskResultId}".format(
            taskResultId=task_result_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.job import Job

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Job)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def restart(
        self: "TaskResultService[codegrade.client.AuthenticatedClient]",
        *,
        task_result_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Restart a task result.

        The restarted task must not be in the `not_started`, `started`, or
        `finished` state.

        :param task_result_id: The task result to restart.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/tasks/{taskResultId}/restart".format(
            taskResultId=task_result_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 204):
            # fmt: off
            # fmt: on
            return parsers.ConstantlyParser(None).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def revoke(
        self: "TaskResultService[codegrade.client.AuthenticatedClient]",
        *,
        task_result_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Revoke a task result.

        The revoked task must be in the \"not\_started\" state.

        :param task_result_id: The task result to revoke.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/tasks/{taskResultId}/revoke".format(
            taskResultId=task_result_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 204):
            # fmt: off
            # fmt: on
            return parsers.ConstantlyParser(None).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )
