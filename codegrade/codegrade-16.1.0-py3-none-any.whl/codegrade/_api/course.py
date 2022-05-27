"""The endpoints for course objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.assignment import Assignment
    from ..models.change_user_role_course_data import ChangeUserRoleCourseData
    from ..models.course_perm_map import CoursePermMap
    from ..models.course_price import CoursePrice
    from ..models.course_register_response import CourseRegisterResponse
    from ..models.course_registration_link import CourseRegistrationLink
    from ..models.course_role import CourseRole
    from ..models.course_role_as_json_with_perms import (
        CourseRoleAsJSONWithPerms,
    )
    from ..models.course_snippet import CourseSnippet
    from ..models.course_statistics_as_json import CourseStatisticsAsJSON
    from ..models.create_assignment_course_data import (
        CreateAssignmentCourseData,
    )
    from ..models.create_course_data import CreateCourseData
    from ..models.create_group_set_course_data import CreateGroupSetCourseData
    from ..models.create_snippet_course_data import CreateSnippetCourseData
    from ..models.email_users_course_data import EmailUsersCourseData
    from ..models.extended_course import ExtendedCourse
    from ..models.extended_course_registration_link import (
        ExtendedCourseRegistrationLink,
    )
    from ..models.extended_work import ExtendedWork
    from ..models.group_set import GroupSet
    from ..models.import_into_course_data import ImportIntoCourseData
    from ..models.job import Job
    from ..models.patch_course_data import PatchCourseData
    from ..models.patch_snippet_course_data import PatchSnippetCourseData
    from ..models.put_enroll_link_course_data import PutEnrollLinkCourseData
    from ..models.put_price_course_data import PutPriceCourseData
    from ..models.register_user_with_link_course_data import (
        RegisterUserWithLinkCourseData,
    )
    from ..models.user import User
    from ..models.user_course import UserCourse


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class CourseService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        offset: Maybe["int"] = Nothing,
        limit: Maybe["int"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedCourse]":
        """Return all Course objects the current user is a member of.

        :param offset: The index of the first course to be returned.
        :param limit: The maximum amount of courses to return.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized courses
        """

        url = "/api/v1/courses/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, offset)).if_just(
            lambda val: params.__setitem__("offset", val)
        )
        maybe_from_nullable(t.cast(t.Any, limit)).if_just(
            lambda val: params.__setitem__("limit", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_course import ExtendedCourse

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedCourse))
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
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateCourseData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourse":
        """Create a new course.

        :param json_body: The body of the request. See
            :class:`.CreateCourseData` for information about the possible
            fields. You can provide this data as a :class:`.CreateCourseData`
            or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialization of the new
                  course
        """

        url = "/api/v1/courses/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def create_snippet(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateSnippetCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CourseSnippet":
        """Add or modify a `CourseSnippet` by key.

        :param json_body: The body of the request. See
            :class:`.CreateSnippetCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateSnippetCourseData` or as a dictionary.
        :param course_id: The id of the course in which you want to create a
            new snippet.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized snippet and return
                  code 201.
        """

        url = "/api/v1/courses/{courseId}/snippet".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 201):
            # fmt: off
            from ..models.course_snippet import CourseSnippet

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CourseSnippet)
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

    def get_group_sets(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[GroupSet]":
        """Get the all the group sets of a given course.

        :param course_id: The id of the course of which the group sets should
            be retrieved.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of group sets.
        """

        url = "/api/v1/courses/{courseId}/group_sets/".format(
            courseId=course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.group_set import GroupSet

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(GroupSet))
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

    def create_group_set(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateGroupSetCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "GroupSet":
        """Create or update a `GroupSet` in the given course id.

        :param json_body: The body of the request. See
            :class:`.CreateGroupSetCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateGroupSetCourseData` or as a dictionary.
        :param course_id: The id of the course in which the group set should be
            created or updated. The course id of a group set cannot change.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created or updated group.
        """

        url = "/api/v1/courses/{courseId}/group_sets/".format(
            courseId=course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.group_set import GroupSet

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(GroupSet)
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

    def get_assignments(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[Assignment]":
        """Get all assignments of the given course.

        The returned assignments are sorted by deadline.

        :param course_id: The id of the course
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the assignments of the given course
                  sorted by deadline of the assignment
        """

        url = "/api/v1/courses/{courseId}/assignments/".format(
            courseId=course_id
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

    def create_assignment(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateAssignmentCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Assignment":
        """Create a new course for the given assignment.

        :param json_body: The body of the request. See
            :class:`.CreateAssignmentCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateAssignmentCourseData` or as a dictionary.
        :param course_id: The course to create an assignment in.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The newly created assignment.
        """

        url = "/api/v1/courses/{courseId}/assignments/".format(
            courseId=course_id
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

    def put_enroll_link(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PutEnrollLinkCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CourseRegistrationLink":
        """Create or edit an enroll link.

        :param json_body: The body of the request. See
            :class:`.PutEnrollLinkCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.PutEnrollLinkCourseData` or as a dictionary.
        :param course_id: The id of the course in which this link should enroll
            users.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created or edited link.
        """

        url = "/api/v1/courses/{courseId}/registration_links/".format(
            courseId=course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_registration_link import CourseRegistrationLink

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CourseRegistrationLink)
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

    def put_price(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PutPriceCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CoursePrice":
        """Update the price of the given course.

        :param json_body: The body of the request. See
            :class:`.PutPriceCourseData` for information about the possible
            fields. You can provide this data as a :class:`.PutPriceCourseData`
            or as a dictionary.
        :param course_id: The id of the course for which you want to update the
            price.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created or updated price.
        """

        url = "/api/v1/courses/{courseId}/price".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_price import CoursePrice

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CoursePrice)
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

    def delete_price(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Update the price of the given course.

        :param course_id: The id of the course for which you want to update the
            price.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created or updated price.
        """

        url = "/api/v1/courses/{courseId}/price".format(courseId=course_id)
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

    def delete_snippet(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        snippet_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete the `CourseSnippet` with the given id.

        :param course_id: The id of the course in which the snippet is located.
        :param snippet_id: The id of the snippet
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An empty response with return code 204
        """

        url = "/api/v1/courses/{courseId}/snippets/{snippetId}".format(
            courseId=course_id, snippetId=snippet_id
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

    def patch_snippet(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchSnippetCourseData"],
        *,
        course_id: "int",
        snippet_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Modify the `CourseSnippet` with the given id.

        :param json_body: The body of the request. See
            :class:`.PatchSnippetCourseData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchSnippetCourseData` or as a dictionary.
        :param course_id: The id of the course in which the course snippet is
            saved.
        :param snippet_id: The id of the snippet to change.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An empty response with return code 204.
        """

        url = "/api/v1/courses/{courseId}/snippets/{snippetId}".format(
            courseId=course_id, snippetId=snippet_id
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

    def delete_role(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        role_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Remove a `CourseRole` from the given `Course`.

        :param course_id: The id of the course
        :param role_id: The id of the role you want to delete
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An empty response with return code 204
        """

        url = "/api/v1/courses/{courseId}/roles/{roleId}".format(
            courseId=course_id, roleId=role_id
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

    def get_course_roles(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[t.Sequence[CourseRoleAsJSONWithPerms], t.Sequence[CourseRole]]":
        """Get a list of all course roles in a given course.

        :param course_id: The id of the course to get the roles for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An array of all course roles for the given course.
        """

        url = "/api/v1/courses/{courseId}/roles/".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_role import CourseRole
            from ..models.course_role_as_json_with_perms import (
                CourseRoleAsJSONWithPerms,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    rqa.List(
                        parsers.ParserFor.make(CourseRoleAsJSONWithPerms)
                    ),
                    rqa.List(parsers.ParserFor.make(CourseRole)),
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

    def get_all_users(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        q: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[t.Sequence[User], t.Sequence[UserCourse]]":
        """Get all users and their role in a course.

        :param course_id: The id of the course
        :param q: Only retrieve users whose name or username matches this
                  value. This will change the output to a list of users.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All users in this course and their role. If you provided the
                  `q` parameter only the user is returned, not their role.
        """

        url = "/api/v1/courses/{courseId}/users/".format(courseId=course_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, q)).if_just(
            lambda val: params.__setitem__("q", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.user import User
            from ..models.user_course import UserCourse

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    rqa.List(parsers.ParserFor.make(User)),
                    rqa.List(parsers.ParserFor.make(UserCourse)),
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

    def change_user_role(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "ChangeUserRoleCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> t.Union["UserCourse", "None"]:
        """Set the `CourseRole` of a user in the given course.

        :param json_body: The body of the request. See
            :class:`.ChangeUserRoleCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.ChangeUserRoleCourseData` or as a dictionary.
        :param course_id: The id of the course in which you want to enroll a
            new user, or change the role of an existing user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: If the user\_id parameter is set in the request the response
                  will be empty with return code 204. Otherwise the response
                  will contain the JSON serialized user and course role with
                  return code 201
        """

        url = "/api/v1/courses/{courseId}/users/".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.user_course import UserCourse

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(UserCourse)
            ).try_parse(resp)
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

    def get(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourse":
        """Get a course by id.

        :param course_id: The id of the course
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized course
        """

        url = "/api/v1/courses/{courseId}".format(courseId=course_id)
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

    def patch(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourse":
        """Update the given course with new values.

        :param json_body: The body of the request. See
            :class:`.PatchCourseData` for information about the possible
            fields. You can provide this data as a :class:`.PatchCourseData` or
            as a dictionary.
        :param course_id: The id of the course you want to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated course, in extended format.
        """

        url = "/api/v1/courses/{courseId}".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def get_snippets(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[CourseSnippet]":
        """Get all snippets of the given course.

        :param course_id: The id of the course from which you want to get the
            snippets.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: An array containing all snippets for the given course.
        """

        url = "/api/v1/courses/{courseId}/snippets/".format(courseId=course_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_snippet import CourseSnippet

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(CourseSnippet))
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

    def get_statistics(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CourseStatisticsAsJSON":
        """Get user statistics of a specific course.

        :param course_id: The id of the course for which you want to get the
            statistics
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the course management statistics
        """

        url = "/api/v1/courses/{courseId}/statistics".format(
            courseId=course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_statistics_as_json import (
                CourseStatisticsAsJSON,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CourseStatisticsAsJSON)
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

    def get_permissions(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CoursePermMap":
        """Get all the permissions of the currently logged in user in this
        course.

        This will return the permission as if you have already paid, even if
        this is not the case.

        :param course_id: The id of the course of which the permissions should
            be retrieved.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A mapping between the permission name and a boolean
                  indicating if the currently logged in user has this
                  permission.
        """

        url = "/api/v1/courses/{courseId}/permissions/".format(
            courseId=course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_perm_map import CoursePermMap

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CoursePermMap)
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

    def get_registration_link(
        self,
        *,
        course_id: "int",
        link_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourseRegistrationLink":
        """Get a registration link.

        This route can be used without logging in, i.e. you don't have to be
        enrolled in the course to use this route. This route will not work for
        expired registration links.

        :param course_id: The id of the course to which the registration link
            is connected.
        :param link_id: The id of the registration link.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The specified registration link.
        """

        url = "/api/v1/courses/{courseId}/registration_links/{linkId}".format(
            courseId=course_id, linkId=link_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_course_registration_link import (
                ExtendedCourseRegistrationLink,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedCourseRegistrationLink)
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
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        *,
        course_id: "int",
        user_id: "int",
        latest_only: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Mapping[str, t.Sequence[ExtendedWork]]":
        """Get all submissions by the given user in this course.

        :param course_id: The id of the course from which you want to get the
            submissions.
        :param user_id: The id of the user of which you want to get the
            submissions.
        :param latest_only: Only get the latest submission of a user. Please
            use this option if at all possible, as students have a tendency to
            submit many attempts and that can make this route quite slow.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A mapping between assignment id and the submissions done in
                  that assignment by the given user. If the `latest_only` query
                  parameter was used the value will still be an array of
                  submissions, but the length will always be one. If the user
                  didn't submit for an assignment the value might be empty or
                  the id of the assignment will be missing from the returned
                  object.
        """

        url = "/api/v1/courses/{courseId}/users/{userId}/submissions/".format(
            courseId=course_id, userId=user_id
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
            from ..models.extended_work import ExtendedWork

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.LookupMapping(
                    rqa.List(parsers.ParserFor.make(ExtendedWork))
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

    def import_into(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "ImportIntoCourseData"],
        *,
        into_course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedCourse":
        """Copy a course into another course.

        :param json_body: The body of the request. See
            :class:`.ImportIntoCourseData` for information about the possible
            fields. You can provide this data as a
            :class:`.ImportIntoCourseData` or as a dictionary.
        :param into_course_id: The course you want to import into.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated course, so the course of which the id was passed
                  in the url.
        """

        url = "/api/v1/courses/{intoCourseId}/copy".format(
            intoCourseId=into_course_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def register_user_with_link(
        self,
        json_body: t.Union[dict, list, "RegisterUserWithLinkCourseData"],
        *,
        course_id: "int",
        link_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CourseRegisterResponse":
        """Register as a new user, and directly enroll in a course.

        :param json_body: The body of the request. See
            :class:`.RegisterUserWithLinkCourseData` for information about the
            possible fields. You can provide this data as a
            :class:`.RegisterUserWithLinkCourseData` or as a dictionary.
        :param course_id: The id of the course to which the registration link
            is connected.
        :param link_id: The id of the registration link.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The access token that the created user can use to log in.
        """

        url = (
            "/api/v1/courses/{courseId}/registration_links/{linkId}/user"
            .format(courseId=course_id, linkId=link_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_register_response import CourseRegisterResponse

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CourseRegisterResponse)
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

    def email_users(
        self: "CourseService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "EmailUsersCourseData"],
        *,
        course_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Job":
        """Sent the authors in this course an email.

        :param json_body: The body of the request. See
            :class:`.EmailUsersCourseData` for information about the possible
            fields. You can provide this data as a
            :class:`.EmailUsersCourseData` or as a dictionary.
        :param course_id: The id of the course in which you want to send the
            emails.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A task result that will send these emails.
        """

        url = "/api/v1/courses/{courseId}/email".format(courseId=course_id)
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
