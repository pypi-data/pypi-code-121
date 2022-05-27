"""The endpoints for auto_test objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.all_auto_test_results import AllAutoTestResults
    from ..models.auto_test import AutoTest
    from ..models.auto_test_result import AutoTestResult
    from ..models.auto_test_set import AutoTestSet
    from ..models.auto_test_suite import AutoTestSuite
    from ..models.copy_auto_test_data import CopyAutoTestData
    from ..models.create_auto_test_data import CreateAutoTestData
    from ..models.create_output_html_proxy_auto_test_data import (
        CreateOutputHtmlProxyAutoTestData,
    )
    from ..models.extended_auto_test_result import ExtendedAutoTestResult
    from ..models.extended_auto_test_run import ExtendedAutoTestRun
    from ..models.patch_auto_test_data import PatchAutoTestData
    from ..models.proxy import Proxy
    from ..models.result_data_get_auto_test_get import ResultDataGetAutoTestGet
    from ..models.update_set_auto_test_data import UpdateSetAutoTestData
    from ..models.update_suite_auto_test_data import UpdateSuiteAutoTestData


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class AutoTestService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def copy(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CopyAutoTestData"],
        *,
        auto_test_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTest":
        """Copy the given `AutoTest` configuration.

        :param json_body: The body of the request. See
            :class:`.CopyAutoTestData` for information about the possible
            fields. You can provide this data as a :class:`.CopyAutoTestData`
            or as a dictionary.
        :param auto_test_id: The id of the `AutoTest` config which should be
            copied.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The copied `AutoTest` configuration.
        """

        url = "/api/v1/auto_tests/{autoTestId}/copy".format(
            autoTestId=auto_test_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test import AutoTest

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTest)
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

    def create(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        multipart_data: t.Union[dict, list, "CreateAutoTestData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTest":
        """Create a new `AutoTest` configuration.

        :param multipart_data: The data that should form the body of the
            request. See :class:`.CreateAutoTestData` for information about the
            possible fields.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The newly created `AutoTest`.
        """

        url = "/api/v1/auto_tests/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url,
                files=utils.to_multipart(utils.to_dict(multipart_data)),
                params=params,
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test import AutoTest

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTest)
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

    def add_set(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTestSet":
        """Create a new set within an `AutoTest`

        :param auto_test_id: The id of the `AutoTest` wherein you want to
            create a set.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The newly created set.
        """

        url = "/api/v1/auto_tests/{autoTestId}/sets/".format(
            autoTestId=auto_test_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test_set import AutoTestSet

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTestSet)
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
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        latest_only: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ResultDataGetAutoTestGet":
        """Get the extended version of an `AutoTest` and its runs.

        :param auto_test_id: The id of the `AutoTest` to get.
        :param latest_only: Only retrieve the results of the latest
            submissions.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The extended serialization of an `AutoTest` and the extended
                  serialization of its runs.
        """

        url = "/api/v1/auto_tests/{autoTestId}".format(autoTestId=auto_test_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "latest_only": utils.to_dict(latest_only),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.result_data_get_auto_test_get import (
                ResultDataGetAutoTestGet,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ResultDataGetAutoTestGet)
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

    def delete(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete the given `AutoTest`.

        This route fails if the `AutoTest` has any runs, which should be
        deleted separately.

        :param auto_test_id: The `AutoTest` that should be deleted.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/auto_tests/{autoTestId}".format(autoTestId=auto_test_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def patch(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        multipart_data: t.Union[dict, list, "PatchAutoTestData"],
        *,
        auto_test_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTest":
        """Update the settings of an `AutoTest` configuration.

        :param multipart_data: The data that should form the body of the
            request. See :class:`.PatchAutoTestData` for information about the
            possible fields.
        :param auto_test_id: The id of the `AutoTest` you want to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated `AutoTest`.
        """

        url = "/api/v1/auto_tests/{autoTestId}".format(autoTestId=auto_test_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url,
                files=utils.to_multipart(utils.to_dict(multipart_data)),
                params=params,
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test import AutoTest

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTest)
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

    def get_run(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        latest_only: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedAutoTestRun":
        """Get the extended version of an `AutoTestRun`.

        The result will also include all the results of the run. If you set the
        `latest_only` query parameter to a truthy value only the results of
        latest submissions will be provided.

        :param auto_test_id: The id of the `AutoTest` which is connected to the
            requested run.
        :param run_id: The id of the run to get.
        :param latest_only: Only retrieve the results for the latest submission
            by a user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The extended version of an `AutoTestRun`.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}".format(
            autoTestId=auto_test_id, runId=run_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "latest_only": utils.to_dict(latest_only),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_auto_test_run import ExtendedAutoTestRun

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedAutoTestRun)
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

    def stop_run(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete an `AutoTest` run, this makes it possible to edit the
        `AutoTest`.

        This also clears the rubric categories filled in by the `AutoTest`.

        :param auto_test_id: The id of the `AutoTest` of which the run should
            be deleted.
        :param run_id: The id of the run which should be deleted.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}".format(
            autoTestId=auto_test_id, runId=run_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def delete_set(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        auto_test_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete an `AutoTestSet` (also known as level).

        :param auto_test_id: The id of the `AutoTest` of the to be deleted set.
        :param auto_test_set_id: The id of the `AutoTestSet` that should be
            deleted.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/auto_tests/{autoTestId}/sets/{autoTestSetId}".format(
            autoTestId=auto_test_id, autoTestSetId=auto_test_set_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def update_set(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "UpdateSetAutoTestData"],
        *,
        auto_test_id: "int",
        auto_test_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTestSet":
        """Update the given `AutoTestSet` (also known as level).

        :param json_body: The body of the request. See
            :class:`.UpdateSetAutoTestData` for information about the possible
            fields. You can provide this data as a
            :class:`.UpdateSetAutoTestData` or as a dictionary.
        :param auto_test_id: The id of the `AutoTest` of the set that should be
            updated.
        :param auto_test_set_id: The id of the `AutoTestSet` that should be
            updated.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated set.
        """

        url = "/api/v1/auto_tests/{autoTestId}/sets/{autoTestSetId}".format(
            autoTestId=auto_test_id, autoTestSetId=auto_test_set_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test_set import AutoTestSet

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTestSet)
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

    def delete_suite(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        test_id: "int",
        set_id: "int",
        suite_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete an `AutoTestSuite` (also known as category).

        :param test_id: The id of the `AutoTest` where the suite is located in.
        :param set_id: The id of the `AutoTestSet` where the suite is located
            in.
        :param suite_id: The id of the `AutoTestSuite` you want to delete.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = (
            "/api/v1/auto_tests/{testId}/sets/{setId}/suites/{suiteId}".format(
                testId=test_id, setId=set_id, suiteId=suite_id
            )
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def get_result(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        result_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedAutoTestResult":
        """Get the extended version of an `AutoTest` result.

        :param auto_test_id: The id of the `AutoTest` in which the result is
            located.
        :param run_id: The id of run in which the result is located.
        :param result_id: The id of the result you want to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The extended version of a `AutoTestResult`.
        """

        url = (
            "/api/v1/auto_tests/{autoTestId}/runs/{runId}/results/{resultId}"
            .format(autoTestId=auto_test_id, runId=run_id, resultId=result_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_auto_test_result import (
                ExtendedAutoTestResult,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedAutoTestResult)
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

    def create_output_html_proxy(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateOutputHtmlProxyAutoTestData"],
        *,
        auto_test_id: "int",
        run_id: "int",
        result_id: "int",
        suite_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Proxy":
        """Create a proxy to view the files of the given AT result through.

        This allows you to view files of an AutoTest result (within a suite)
        without authentication for a limited time.

        :param json_body: The body of the request. See
            :class:`.CreateOutputHtmlProxyAutoTestData` for information about
            the possible fields. You can provide this data as a
            :class:`.CreateOutputHtmlProxyAutoTestData` or as a dictionary.
        :param auto_test_id: The id of the AutoTest in which the result is
            located.
        :param run_id: The id of run in which the result is located.
        :param result_id: The id of the result from which you want to get the
            files.
        :param suite_id: The suite from which you want to proxy the output
            files.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created proxy.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}/results/{resultId}/suites/{suiteId}/proxy".format(
            autoTestId=auto_test_id,
            runId=run_id,
            resultId=result_id,
            suiteId=suite_id,
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.proxy import Proxy

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Proxy)
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

    def get_result_by_submission(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedAutoTestResult":
        """Get the `AutoTest` result for a submission.

        :param auto_test_id: The id of the `AutoTest` in which to get the
            result.
        :param run_id: The id of the `AutoTestRun` in which to get the result.
        :param submission_id: The id of the submission from which you want to
            get the result.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The `AutoTest` result for the given data.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}/submissions/{submissionId}/result".format(
            autoTestId=auto_test_id, runId=run_id, submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_auto_test_result import (
                ExtendedAutoTestResult,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedAutoTestResult)
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

    def get_results_by_user(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[AutoTestResult]":
        """Get all `AutoTest` results for a given user.

        If you don't have permission to see the results of the requested user
        an empty list will be returned.

        :param auto_test_id: The id of the `AutoTest` in which to get the
            results.
        :param run_id: The id of the `AutoTestRun` in which to get the results.
        :param user_id: The id of the user of which we should get the results.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The list of `AutoTest` results for the given user, sorted
                  from oldest to latest.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}/users/{userId}/results/".format(
            autoTestId=auto_test_id, runId=run_id, userId=user_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test_result import AutoTestResult

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(AutoTestResult))
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

    def get_attachment(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        step_result_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "bytes":
        """Get the attachment of an `AutoTest` step.

        :param auto_test_id: The id of the `AutoTest` in which the result is
            located.
        :param run_id: The id of run in which the result is located.
        :param step_result_id: The id of the step result of which you want the
            attachment.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The attachment data, as an application/octet-stream.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}/step_results/{stepResultId}/attachment".format(
            autoTestId=auto_test_id, runId=run_id, stepResultId=step_result_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            # fmt: on
            return parsers.ResponsePropertyParser("content", bytes).try_parse(
                resp
            )

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

    def get_fixture(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        fixture_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "bytes":
        """Get the contents of the given `AutoTestFixture`.

        :param auto_test_id: The `AutoTest` this fixture is linked to.
        :param fixture_id: The id of the fixture which you want the content.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The content of the given fixture.
        """

        url = "/api/v1/auto_tests/{autoTestId}/fixtures/{fixtureId}".format(
            autoTestId=auto_test_id, fixtureId=fixture_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            # fmt: on
            return parsers.ResponsePropertyParser("content", bytes).try_parse(
                resp
            )

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

    def get_not_started_results(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        offset: "int" = 0,
        limit: "int" = 50,
        state: "t.Literal['not_started']" = "not_started",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AllAutoTestResults":
        """Get all `AutoTest` results on this instance.

        :param offset: First non started result to get.
        :param limit: Amount of non started results to get.
        :param state: The state the results should be in, currently only
            `not_started` is supported.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The (limited) results of this instance, and the total amount
                  of non requested results.
        """

        url = "/api/v1/auto_test_results/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "offset": utils.to_dict(offset),
            "limit": utils.to_dict(limit),
            "state": utils.to_dict(state),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.all_auto_test_results import AllAutoTestResults

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AllAutoTestResults)
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

    def hide_fixture(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        fixture_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Change the visibility of the given fixture.

        Doing a `POST` request to this route will hide the fixture, doing a
        `DELETE` request to this route will set `hidden` to `False`.

        :param auto_test_id: The `AutoTest` this fixture is linked to.
        :param fixture_id: The fixture which you to hide or show.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = (
            "/api/v1/auto_tests/{autoTestId}/fixtures/{fixtureId}/hide".format(
                autoTestId=auto_test_id, fixtureId=fixture_id
            )
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

    def show_fixture(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        fixture_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Change the visibility of the given fixture.

        Doing a `POST` request to this route will hide the fixture, doing a
        `DELETE` request to this route will set `hidden` to `False`.

        :param auto_test_id: The `AutoTest` this fixture is linked to.
        :param fixture_id: The fixture which you to hide or show.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = (
            "/api/v1/auto_tests/{autoTestId}/fixtures/{fixtureId}/hide".format(
                autoTestId=auto_test_id, fixtureId=fixture_id
            )
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def restart_result(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        run_id: "int",
        result_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedAutoTestResult":
        """Restart an `AutoTest` result.

        :param auto_test_id: The id of the `AutoTest` in which the result is
            located.
        :param run_id: The id of run in which the result is located.
        :param result_id: The id of the result you want to restart.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The extended version of a `AutoTestResult`.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/{runId}/results/{resultId}/restart".format(
            autoTestId=auto_test_id, runId=run_id, resultId=result_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_auto_test_result import (
                ExtendedAutoTestResult,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedAutoTestResult)
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

    def start_run(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        *,
        auto_test_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedAutoTestRun, t.Mapping[str, t.Literal['']]]":
        """Start a run for the given `AutoTest`.

        :param auto_test_id: The id of the `AutoTest` for which you want to
            start a run.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The started run or a empty mapping if you do not have
                  permission to see `AutoTest` runs.
        """

        url = "/api/v1/auto_tests/{autoTestId}/runs/".format(
            autoTestId=auto_test_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_auto_test_run import ExtendedAutoTestRun

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedAutoTestRun),
                    rqa.LookupMapping(rqa.StringEnum("")),
                )
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

    def update_suite(
        self: "AutoTestService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "UpdateSuiteAutoTestData"],
        *,
        auto_test_id: "int",
        set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTestSuite":
        """Update or create a `AutoTestSuite` (also known as category)

        :param json_body: The body of the request. See
            :class:`.UpdateSuiteAutoTestData` for information about the
            possible fields. You can provide this data as a
            :class:`.UpdateSuiteAutoTestData` or as a dictionary.
        :param auto_test_id: The id of the `AutoTest` in which this suite
            should be created.
        :param set_id: The id the `AutoTestSet` in which this suite should be
            created.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just updated or created `AutoTestSuite`.
        """

        url = "/api/v1/auto_tests/{autoTestId}/sets/{setId}/suites/".format(
            autoTestId=auto_test_id, setId=set_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.auto_test_suite import AutoTestSuite

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AutoTestSuite)
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
