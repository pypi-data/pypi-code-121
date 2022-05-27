"""The endpoints for submission objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.create_proxy_submission_data import CreateProxySubmissionData
    from ..models.extended_work import ExtendedWork
    from ..models.feedback_with_replies import FeedbackWithReplies
    from ..models.feedback_without_replies import FeedbackWithoutReplies
    from ..models.grade_history import GradeHistory
    from ..models.mirror_file_result import MirrorFileResult
    from ..models.patch_grader_submission_data import PatchGraderSubmissionData
    from ..models.patch_rubric_result_submission_data import (
        PatchRubricResultSubmissionData,
    )
    from ..models.patch_submission_data import PatchSubmissionData
    from ..models.proxy import Proxy
    from ..models.root_file_trees_json import RootFileTreesJSON
    from ..models.work_rubric_result_as_json import WorkRubricResultAsJSON


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class SubmissionService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def create_proxy(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateProxySubmissionData"],
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Proxy":
        """Create a proxy to view the files of the given submission through.

        This allows you to view files of a submission without authentication
        for a limited time.

        :param json_body: The body of the request. See
            :class:`.CreateProxySubmissionData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateProxySubmissionData` or as a dictionary.
        :param submission_id: The submission for which the proxy should be
            created.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created proxy.
        """

        url = "/api/v1/submissions/{submissionId}/proxy".format(
            submissionId=submission_id
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

    def get(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        *,
        submission_id: "int",
        type: "t.Literal['default', 'feedback', 'zip']" = "default",
        owner: "t.Literal['auto', 'student', 'teacher']" = "auto",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedWork, MirrorFileResult]":
        """Get the given submission (also called work) by id.

        :param submission_id: The id of the submission
        :param type: If passed this cause you not to receive a submission
            object. What you will receive will depend on the value passed. If
            you pass `zip` you will receive a zip file with all the files of
            the submission. If you pass `feedback` you will receive a text file
            with a textual representation of all the feedback given on this
            submission.
        :param owner: This query parameter is only used when `type=='zip'`. It
            will determine which revision is used to generate the zip file.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested submission, or one of the other types as
                  requested by the `type` query parameter.
        """

        url = "/api/v1/submissions/{submissionId}".format(
            submissionId=submission_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "type": utils.to_dict(type),
            "owner": utils.to_dict(owner),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_work import ExtendedWork
            from ..models.mirror_file_result import MirrorFileResult

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedWork),
                    parsers.ParserFor.make(MirrorFileResult),
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

    def delete(
        self,
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete a submission and all its files.

        :param submission_id: The submission to delete.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing
        """

        url = "/api/v1/submissions/{submissionId}".format(
            submissionId=submission_id
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

    def patch(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchSubmissionData"],
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedWork":
        """Update the given submission with new values.

        :param json_body: The body of the request. See
            :class:`.PatchSubmissionData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchSubmissionData` or as a dictionary.
        :param submission_id: The id of the submission.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated submission.
        """

        url = "/api/v1/submissions/{submissionId}".format(
            submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_work import ExtendedWork

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedWork)
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

    def delete_grader(
        self,
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Change the assigned grader of the given submission.

        :param submission_id: The id of the submission.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Empty response and a 204 status.
        """

        url = "/api/v1/submissions/{submissionId}/grader".format(
            submissionId=submission_id
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

    def patch_grader(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchGraderSubmissionData"],
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Change the assigned grader of the given submission.

        :param json_body: The body of the request. See
            :class:`.PatchGraderSubmissionData` for information about the
            possible fields. You can provide this data as a
            :class:`.PatchGraderSubmissionData` or as a dictionary.
        :param submission_id: The id of the submission.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Empty response and a 204 status.
        """

        url = "/api/v1/submissions/{submissionId}/grader".format(
            submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def get_feedback(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        *,
        submission_id: "int",
        with_replies: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[FeedbackWithReplies, FeedbackWithoutReplies]":
        """Get all feedback for a submission

        :param submission_id: The submission of which you want to get the
            feedback.
        :param with_replies: Do you want to include replies in with your
            comments? Starting with version "O.1" the default value will change
            to `True`.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The feedback of this submission.
        """

        url = "/api/v1/submissions/{submissionId}/feedbacks/".format(
            submissionId=submission_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "with_replies": utils.to_dict(with_replies),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.feedback_with_replies import FeedbackWithReplies
            from ..models.feedback_without_replies import FeedbackWithoutReplies

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(FeedbackWithReplies),
                    parsers.ParserFor.make(FeedbackWithoutReplies),
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

    def get_grade_history(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[GradeHistory]":
        """Get the grade history for the given submission.

        :param submission_id: The submission for which you want to get the
            grade history.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All the `GradeHistory` objects, which describe the history of
                  this grade.
        """

        url = "/api/v1/submissions/{submissionId}/grade_history/".format(
            submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.grade_history import GradeHistory

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(GradeHistory))
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

    def get_root_file_trees(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "RootFileTreesJSON":
        """Get all the file trees of a submission.

        :param submission_id: The id of the submission of which you want to get
            the file trees.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The student and teacher file tree, from the base/root
                  directory of the submission.
        """

        url = "/api/v1/submissions/{submissionId}/root_file_trees/".format(
            submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.root_file_trees_json import RootFileTreesJSON

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(RootFileTreesJSON)
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

    def get_rubric_result(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        *,
        submission_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "WorkRubricResultAsJSON":
        """Get the full rubric result of the given submission (work).

        :param submission_id: The id of the submission
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The rubric result of the given submission, which also
                  contains the rubric.
        """

        url = "/api/v1/submissions/{submissionId}/rubrics/".format(
            submissionId=submission_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.work_rubric_result_as_json import (
                WorkRubricResultAsJSON,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(WorkRubricResultAsJSON)
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

    def patch_rubric_result(
        self: "SubmissionService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchRubricResultSubmissionData"],
        *,
        submission_id: "int",
        copy_locked_items: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedWork":
        """Select the given rubric items for the given submission.

        :param json_body: The body of the request. See
            :class:`.PatchRubricResultSubmissionData` for information about the
            possible fields. You can provide this data as a
            :class:`.PatchRubricResultSubmissionData` or as a dictionary.
        :param submission_id: The submission to unselect the item for.
        :param copy_locked_items: Should we maintain the selected items in
            locked rubric rows.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/submissions/{submissionId}/rubricitems/".format(
            submissionId=submission_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "copy_locked_items": utils.to_dict(copy_locked_items),
        }

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_work import ExtendedWork

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedWork)
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
