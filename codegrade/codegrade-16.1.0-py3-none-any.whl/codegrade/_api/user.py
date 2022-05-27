"""The endpoints for user objects.

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

    from ..models.coupon_usage import CouponUsage
    from ..models.extended_transaction import ExtendedTransaction
    from ..models.extended_user import ExtendedUser
    from ..models.login_user_data import LoginUserData
    from ..models.patch_user_data import PatchUserData
    from ..models.register_user_data import RegisterUserData
    from ..models.result_data_post_user_login import ResultDataPostUserLogin
    from ..models.result_data_post_user_register import (
        ResultDataPostUserRegister,
    )
    from ..models.user import User


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class UserService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def patch(
        self: "UserService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchUserData"],
        *,
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedUser":
        """Update the attributes of a user.

        :param json_body: The body of the request. See :class:`.PatchUserData`
            for information about the possible fields. You can provide this
            data as a :class:`.PatchUserData` or as a dictionary.
        :param user_id: The id of the user you want to change. Currently this
            can only be your own user id.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated user.
        """

        url = "/api/v1/users/{userId}".format(userId=user_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_user import ExtendedUser

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedUser)
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

    def get_coupon_usages(
        self: "UserService[codegrade.client.AuthenticatedClient]",
        *,
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[CouponUsage]":
        """Get all the coupons used for the specified user.

        :param user_id: The user to get the coupons used for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All coupons used for the given user.
        """

        url = "/api/v1/users/{userId}/coupon_usages/".format(userId=user_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.coupon_usage import CouponUsage

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(CouponUsage))
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

    def get_transactions(
        self: "UserService[codegrade.client.AuthenticatedClient]",
        *,
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedTransaction]":
        """Get all transactions for the specified user.

        :param user_id: The user to get the transactions for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All transactions for the given user.
        """

        url = "/api/v1/users/{userId}/transactions/".format(userId=user_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_transaction import ExtendedTransaction

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedTransaction))
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
        self: "UserService[codegrade.client.AuthenticatedClient]",
        *,
        type: "t.Literal['default', 'extended', 'roles']" = "default",
        extended: "bool" = False,
        with_permissions: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedUser, User, t.Mapping[str, str]]":
        """Get the info of the currently logged in user.

        :param type: If this is `roles` a mapping between course\_id and role
            name will be returned, if this is `extended` an `ExtendedUser`
            instead of a `User` will be returned.
        :param extended: If `true` this has the same effect as setting `type`
            to `extended`.
        :param with_permissions: Setting this to true will add the key
            `permissions` to the user. The value will be a mapping indicating
            which global permissions this user has.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized user
        """

        url = "/api/v1/login"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "type": utils.to_dict(type),
            "extended": utils.to_dict(extended),
            "with_permissions": utils.to_dict(with_permissions),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_user import ExtendedUser
            from ..models.user import User

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedUser),
                    parsers.ParserFor.make(User),
                    rqa.LookupMapping(rqa.SimpleValue.str),
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

    def login(
        self,
        json_body: t.Union[dict, list, "LoginUserData"],
        *,
        with_permissions: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ResultDataPostUserLogin":
        """Login using your username and password.

        `permissions` to the user. The value will be a mapping indicating which
        global permissions this user has.

        :param json_body: The body of the request. See :class:`.LoginUserData`
            for information about the possible fields. You can provide this
            data as a :class:`.LoginUserData` or as a dictionary.
        :param with_permissions: Return the global permissions of the newly
            logged in user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized user
        """

        url = "/api/v1/login"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "with_permissions": utils.to_dict(with_permissions),
        }

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.result_data_post_user_login import (
                ResultDataPostUserLogin,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ResultDataPostUserLogin)
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

    def register(
        self,
        json_body: t.Union[dict, list, "RegisterUserData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ResultDataPostUserRegister":
        """Create a new user.

        :param json_body: The body of the request. See
            :class:`.RegisterUserData` for information about the possible
            fields. You can provide this data as a :class:`.RegisterUserData`
            or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The registered user and an `access_token` that can be used to
                  perform requests as this new user.
        """

        url = "/api/v1/user"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.result_data_post_user_register import (
                ResultDataPostUserRegister,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ResultDataPostUserRegister)
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

    def search(
        self: "UserService[codegrade.client.AuthenticatedClient]",
        *,
        q: "str",
        exclude_course: Maybe["int"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[User]":
        """Search for a user by name and username.

        :param q: The string to search for, all SQL wildcard are escaped and
                  spaces are replaced by wildcards.
        :param exclude_course: Exclude all users that are in the given course
            from the search results. You need the permission
            `can_list_course_users` on this course to use this parameter.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The users that match the given query string.
        """

        url = "/api/v1/users/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "q": utils.to_dict(q),
        }
        maybe_from_nullable(t.cast(t.Any, exclude_course)).if_just(
            lambda val: params.__setitem__("exclude_course", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.user import User

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(User))
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
