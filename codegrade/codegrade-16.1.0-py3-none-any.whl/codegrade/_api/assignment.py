"""The endpoints for assignment objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers, utils
from ..models.ignore_handling import IgnoreHandling

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.assignment import Assignment
    from ..models.assignment_feedback import AssignmentFeedback
    from ..models.assignment_grader import AssignmentGrader
    from ..models.assignment_peer_feedback_connection import (
        AssignmentPeerFeedbackConnection,
    )
    from ..models.assignment_peer_feedback_settings import (
        AssignmentPeerFeedbackSettings,
    )
    from ..models.assignment_template import AssignmentTemplate
    from ..models.auto_test import AutoTest
    from ..models.comment_base import CommentBase
    from ..models.copy_rubric_assignment_data import CopyRubricAssignmentData
    from ..models.export_assignment_data import ExportAssignmentData
    from ..models.extended_course import ExtendedCourse
    from ..models.extended_work import ExtendedWork
    from ..models.import_into_assignment_data import ImportIntoAssignmentData
    from ..models.job import Job
    from ..models.patch_assignment_data import PatchAssignmentData
    from ..models.patch_rubric_category_type_assignment_data import (
        PatchRubricCategoryTypeAssignmentData,
    )
    from ..models.patch_submit_types_assignment_data import (
        PatchSubmitTypesAssignmentData,
    )
    from ..models.plagiarism_run import PlagiarismRun
    from ..models.put_rubric_assignment_data import PutRubricAssignmentData
    from ..models.rubric_row_base import RubricRowBase
    from ..models.update_peer_feedback_settings_assignment_data import (
        UpdatePeerFeedbackSettingsAssignmentData,
    )
    from ..models.upload_submission_assignment_data import (
        UploadSubmissionAssignmentData,
    )
    from ..models.webhook_base import WebhookBase
    from ..models.work import Work


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class AssignmentService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_rubric(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[RubricRowBase]":
        """Return the rubric corresponding to the given `assignment_id`.

        :param assignment_id: The id of the assignment.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of `RubricRow` items.
        """

        url = "/api/v1/assignments/{assignmentId}/rubrics/".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.rubric_row_base import RubricRowBase

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(RubricRowBase))
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

    def put_rubric(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PutRubricAssignmentData"],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[RubricRowBase]":
        """Add or update rubric of an assignment.

        :param json_body: The body of the request. See
            :class:`.PutRubricAssignmentData` for information about the
            possible fields. You can provide this data as a
            :class:`.PutRubricAssignmentData` or as a dictionary.
        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated or created rubric.
        """

        url = "/api/v1/assignments/{assignmentId}/rubrics/".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.rubric_row_base import RubricRowBase

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(RubricRowBase))
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

    def delete_rubric(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete the rubric for the given assignment.

        :param assignment_id: The id of the `Assignment` whose rubric should be
            deleted.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/assignments/{assignmentId}/rubrics/".format(
            assignmentId=assignment_id
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

    def patch_rubric_category_type(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[
            dict, list, "PatchRubricCategoryTypeAssignmentData"
        ],
        *,
        assignment_id: "int",
        rubric_category_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "RubricRowBase":
        """Change the type of a rubric category.

        :param json_body: The body of the request. See
            :class:`.PatchRubricCategoryTypeAssignmentData` for information
            about the possible fields. You can provide this data as a
            :class:`.PatchRubricCategoryTypeAssignmentData` or as a dictionary.
        :param assignment_id: The assignment of the rubric category.
        :param rubric_category_id: The rubric category you want to change the
            type of.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated rubric row.
        """

        url = "/api/v1/assignments/{assignmentId}/rubrics/{rubricCategoryId}/type".format(
            assignmentId=assignment_id, rubricCategoryId=rubric_category_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.rubric_row_base import RubricRowBase

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(RubricRowBase)
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
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Assignment":
        """Return the given `Assignment`.

        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized assignment
        """

        url = "/api/v1/assignments/{assignmentId}".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment import Assignment

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Assignment)
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
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete a given `Assignment`.

        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/assignments/{assignmentId}".format(
            assignmentId=assignment_id
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
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchAssignmentData"],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Assignment":
        """Update the given assignment with new values.

        :param json_body: The body of the request. See
            :class:`.PatchAssignmentData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchAssignmentData` or as a dictionary.
        :param assignment_id: The id of the assignment you want to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated assignment.
        """

        url = "/api/v1/assignments/{assignmentId}".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment import Assignment

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Assignment)
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

    def get_template(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AssignmentTemplate":
        """Return the template corresponding to the given `assignment_id`.

        :param assignment_id: The id of the assignment.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The template for this assignment.
        """

        url = "/api/v1/assignments/{assignmentId}/template".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_template import AssignmentTemplate

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AssignmentTemplate)
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

    def delete_template(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete the template corresponding to the given `assignment_id`.

        :param assignment_id: The id of the assignment.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/assignments/{assignmentId}/template".format(
            assignmentId=assignment_id
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

    def update_peer_feedback_settings(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[
            dict, list, "UpdatePeerFeedbackSettingsAssignmentData"
        ],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AssignmentPeerFeedbackSettings":
        """Enable peer feedback for an assignment.

        :param json_body: The body of the request. See
            :class:`.UpdatePeerFeedbackSettingsAssignmentData` for information
            about the possible fields. You can provide this data as a
            :class:`.UpdatePeerFeedbackSettingsAssignmentData` or as a
            dictionary.
        :param assignment_id: The id of the assignment for which you want to
            enable peer feedback.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just created peer feedback settings.
        """

        url = (
            "/api/v1/assignments/{assignmentId}/peer_feedback_settings".format(
                assignmentId=assignment_id
            )
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_peer_feedback_settings import (
                AssignmentPeerFeedbackSettings,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AssignmentPeerFeedbackSettings)
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

    def disable_peer_feedback(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Disabled peer feedback for an assignment.

        :param assignment_id: The id of the assignment for which you want to
            disable peer feedback.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing; an empty response.
        """

        url = (
            "/api/v1/assignments/{assignmentId}/peer_feedback_settings".format(
                assignmentId=assignment_id
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

    def export(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "ExportAssignmentData"],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Job":
        """Generate a CSV report for this assignment.

        :param json_body: The body of the request. See
            :class:`.ExportAssignmentData` for information about the possible
            fields. You can provide this data as a
            :class:`.ExportAssignmentData` or as a dictionary.
        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A CSV report for this assignment.
        """

        url = "/api/v1/assignments/{assignmentId}/export".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def get_all(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        only_with_rubric: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[Assignment]":
        """Get all the assignments that the current user can see.

        :param only_with_rubric: When `True` only assignments that have a
            rubric will be returned.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All assignments (with a rubric if specified) that the current
                  user can see.
        """

        url = "/api/v1/assignments/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "only_with_rubric": utils.to_dict(only_with_rubric),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment import Assignment

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(Assignment))
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

    def get_all_graders(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[AssignmentGrader]":
        """Gets a list of all users that can grade in the given assignment.

        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized graders.
        """

        url = "/api/v1/assignments/{assignmentId}/graders/".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_grader import AssignmentGrader

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(AssignmentGrader))
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

    def get_submissions_by_user(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedWork]":
        """Return all submissions by the given user in the given assignment.

        This always returns extended version of the submissions.

        :param assignment_id: The id of the assignment
        :param user_id: The user of which you want to get the submissions.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized submissions.
        """

        url = (
            "/api/v1/assignments/{assignmentId}/users/{userId}/submissions/"
            .format(assignmentId=assignment_id, userId=user_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_work import ExtendedWork

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedWork))
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

    def get_all_submissions(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extended: "bool" = False,
        latest_only: "bool" = True,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[t.Sequence[ExtendedWork], t.Sequence[Work]]":
        """Return all submissions for the given assignment.

        :param assignment_id: The id of the assignment
        :param extended: Whether to get extended or normal submissions.
        :param latest_only: Only get the latest submission of a user. Please
            use this option if at all possible, as students have a tendency to
            submit many attempts and that can make this route quite slow. The
            default value was changed to `True` in version "O".
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized submissions.
        """

        url = "/api/v1/assignments/{assignmentId}/submissions/".format(
            assignmentId=assignment_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "extended": utils.to_dict(extended),
            "latest_only": utils.to_dict(latest_only),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_work import ExtendedWork
            from ..models.work import Work

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    rqa.List(parsers.ParserFor.make(ExtendedWork)),
                    rqa.List(parsers.ParserFor.make(Work)),
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

    def get_all_feedback(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Mapping[str, AssignmentFeedback]":
        """Get all feedbacks for all the latest submissions for a given
        assignment.

        :param assignment_id: The assignment to query for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A mapping between the id of the submission and a
                  `AssignmentFeeback` object.
        """

        url = "/api/v1/assignments/{assignmentId}/feedbacks/".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_feedback import AssignmentFeedback

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.LookupMapping(parsers.ParserFor.make(AssignmentFeedback))
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

    def get_auto_test(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AutoTest":
        """Get the `AutoTest` for this assignment.

        :param assignment_id: The id of the assignment from which you want to
            get the `AutoTest`.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The `AutoTest` for the given assignment, if it has an
                  `AutoTest`.
        """

        url = "/api/v1/assignments/{assignmentId}/auto_test".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
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

    def get_comments_by_user(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[CommentBase]":
        """Get all the comments threads that a user replied on.

        This route is especially useful in the context of peer feedback. With
        this route you can get all the comments placed by the student, so you
        don't have to get all the submissions (including old ones) by the peer
        feedback subjects.

        :param assignment_id: The assignment from which you want to get the
            threads.
        :param user_id: The id of the user from which you want to get the
            threads.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of comments that all have at least one reply by the
                  given user. There might be replies missing from these bases
                  if these replies where not given by the user with id
                  `user_id`, however no guarantee is made that all replies are
                  by the user with id `user_id`.
        """

        url = (
            "/api/v1/assignments/{assignmentId}/users/{userId}/comments/"
            .format(assignmentId=assignment_id, userId=user_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.comment_base import CommentBaseParser

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(CommentBaseParser)
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

    def get_course(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourse":
        """Get the course connected to an assignment.

        :param assignment_id: The id of the assignment from which you want to
            get the course.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized course.
        """

        url = "/api/v1/assignments/{assignmentId}/course".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_course import ExtendedCourse

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedCourse)
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

    def get_webhook_settings(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        webhook_type: "t.Literal['git']",
        author_id: Maybe["int"] = Nothing,
        is_test_submission: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "WebhookBase":
        """Create or get the webhook settings to hand-in submissions.

        You can select the user for which the webhook should hand-in using the
        exact same query parameters as the route to upload a submission.

        :param assignment_id: The assignment for which the webhook should
            hand-in submissions.
        :param webhook_type: The webhook type, currently only `git` is
            supported, which works for both GitLab and GitHub.
        :param author_id: The id of the user for which we should get the
            webhook settings. If not given defaults to the current user.
        :param is_test_submission: Should we get the webhook settings for the
            test student.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A serialized form of a webhook, which contains all data
                  needed to add the webhook to your provider.
        """

        url = "/api/v1/assignments/{assignmentId}/webhook_settings".format(
            assignmentId=assignment_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "webhook_type": utils.to_dict(webhook_type),
            "is_test_submission": utils.to_dict(is_test_submission),
        }
        maybe_from_nullable(t.cast(t.Any, author_id)).if_just(
            lambda val: params.__setitem__("author_id", val)
        )

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.webhook_base import WebhookBase

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(WebhookBase)
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

    def get_member_states(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        group_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Mapping[str, bool]":
        """Get the LTI states for the members of a group for the given
        assignment.

        :param assignment_id: The assignment for which the LTI states should be
            given.
        :param group_id: The group for which the states should be returned.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A mapping between user id and a boolean indicating if we can
                  already passback grades for this user. If the assignment is
                  any LTI assignment and any of the values in this mapping is
                  `False` trying to submit anyway will result in a failure.
        """

        url = "/api/v1/assignments/{assignmentId}/groups/{groupId}/member_states/".format(
            assignmentId=assignment_id, groupId=group_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            # fmt: on
            return parsers.JsonResponseParser(
                rqa.LookupMapping(rqa.SimpleValue.bool)
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

    def get_peer_feedback_subjects(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[AssignmentPeerFeedbackConnection]":
        """Get the peer feedback subjects for a given user.

        :param assignment_id: The id of the assignment in which you want to get
            the peer feedback subjects.
        :param user_id: The id of the user from which you want to retrieve the
            peer feedback subjects.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The peer feedback subjects. If the deadline has not expired,
                  or if the assignment is not a peer feedback assignment an
                  empty list will be returned.
        """

        url = "/api/v1/assignments/{assignmentId}/users/{userId}/peer_feedback_subjects/".format(
            assignmentId=assignment_id, userId=user_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_peer_feedback_connection import (
                AssignmentPeerFeedbackConnection,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(
                    parsers.ParserFor.make(AssignmentPeerFeedbackConnection)
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

    def get_all_plagiarism_runs(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[PlagiarismRun]":
        """Get all plagiarism runs for the given assignment.

        :param assignment_id: The id of the assignment
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized list of plagiarism
                  runs.
        """

        url = "/api/v1/assignments/{assignmentId}/plagiarism/".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.plagiarism_run import PlagiarismRun

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(PlagiarismRun))
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

    def import_into(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "ImportIntoAssignmentData"],
        *,
        into_assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Assignment":
        """Import an assignment into another assignment.

        :param json_body: The body of the request. See
            :class:`.ImportIntoAssignmentData` for information about the
            possible fields. You can provide this data as a
            :class:`.ImportIntoAssignmentData` or as a dictionary.
        :param into_assignment_id: The assignment you want to import into.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated assignment, so the assignment which was imported
                  into.
        """

        url = "/api/v1/assignments/{intoAssignmentId}/import".format(
            intoAssignmentId=into_assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment import Assignment

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Assignment)
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

    def copy_rubric(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CopyRubricAssignmentData"],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[RubricRowBase]":
        """Import a rubric from a different assignment.

        :param json_body: The body of the request. See
            :class:`.CopyRubricAssignmentData` for information about the
            possible fields. You can provide this data as a
            :class:`.CopyRubricAssignmentData` or as a dictionary.
        :param assignment_id: The id of the assignment in which you want to
            import the rubric. This assignment shouldn't have a rubric.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The rubric rows of the assignment in which the rubric was
                  imported, so the assignment with id `assignment_id` and not
                  `old_assignment_id`.
        """

        url = "/api/v1/assignments/{assignmentId}/rubric".format(
            assignmentId=assignment_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.rubric_row_base import RubricRowBase

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(RubricRowBase))
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

    def mark_grader_as_done(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        grader_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Indicate that the given grader is done grading the given assignment.

        :param assignment_id: The id of the assignment the grader is done
            grading.
        :param grader_id: The id of the `User` that is done grading.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An empty response with return code 204
        """

        url = (
            "/api/v1/assignments/{assignmentId}/graders/{graderId}/done"
            .format(assignmentId=assignment_id, graderId=grader_id)
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

    def mark_grader_as_not_done(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        *,
        assignment_id: "int",
        grader_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Indicate that the given grader is not yet done grading the given
        assignment.

        :param assignment_id: The id of the assignment the grader is not yet
            done grading.
        :param grader_id: The id of the `User` that is not yet done grading.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An empty response with return code 204
        """

        url = (
            "/api/v1/assignments/{assignmentId}/graders/{graderId}/done"
            .format(assignmentId=assignment_id, graderId=grader_id)
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

    def patch_submit_types(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        multipart_data: t.Union[dict, list, "PatchSubmitTypesAssignmentData"],
        *,
        assignment_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Assignment":
        """Update the given assignment editor template with new files.

        How this route deals with existing editor templates when submitting is
        still experimental and might change in an upcoming release.

        :param multipart_data: The data that should form the body of the
            request. See :class:`.PatchSubmitTypesAssignmentData` for
            information about the possible fields.
        :param assignment_id: The id of the assignment for which you want to
            update the editor template.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated assignment.
        """

        url = "/api/v1/assignments/{assignmentId}/submit_types".format(
            assignmentId=assignment_id
        )
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
            from ..models.assignment import Assignment

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Assignment)
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

    def upload_submission(
        self: "AssignmentService[codegrade.client.AuthenticatedClient]",
        multipart_data: t.Union[dict, list, "UploadSubmissionAssignmentData"],
        *,
        assignment_id: "int",
        author_id: Maybe["int"] = Nothing,
        is_test_submission: "bool" = False,
        ignored_files: "IgnoreHandling" = IgnoreHandling.keep,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedWork":
        """Upload one or more files as `Work` to the given `Assignment`.

        :param multipart_data: The data that should form the body of the
            request. See :class:`.UploadSubmissionAssignmentData` for
            information about the possible fields.
        :param assignment_id: The id of the assignment
        :param author_id: The id of the user for which we should get the
            webhook settings. If not given defaults to the current user.
        :param is_test_submission: Should we get the webhook settings for the
            test student.
        :param ignored_files: How to handle ignored files. The options are:
            `keep`: this the default, sipmly do nothing about ignored files.
            `delete`: delete the ignored files. `error`: return an error when
            there are ignored files in the archive.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created work.
        """

        url = "/api/v1/assignments/{assignmentId}/submission".format(
            assignmentId=assignment_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "is_test_submission": utils.to_dict(is_test_submission),
            "ignored_files": utils.to_dict(ignored_files),
        }
        maybe_from_nullable(t.cast(t.Any, author_id)).if_just(
            lambda val: params.__setitem__("author_id", val)
        )

        with self.__client as client:
            resp = client.http.post(
                url=url,
                files=utils.to_multipart(utils.to_dict(multipart_data)),
                params=params,
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 201):
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
