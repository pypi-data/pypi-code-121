"""The endpoints for git_provider objects.

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

    from ..models.connect_repository_git_provider_data import (
        ConnectRepositoryGitProviderData,
    )
    from ..models.create_repository_git_provider_data import (
        CreateRepositoryGitProviderData,
    )
    from ..models.git_repositories_page import GitRepositoriesPage
    from ..models.job import Job


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class GitProviderService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def connect_repository(
        self: "GitProviderService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "ConnectRepositoryGitProviderData"],
        *,
        provider_id: "str",
        token_id: "str",
        repository_id: "str",
        is_test_student: "bool",
        author_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Job":
        """Connect an existing repository to an assignment.

        :param json_body: The body of the request. See
            :class:`.ConnectRepositoryGitProviderData` for information about
            the possible fields. You can provide this data as a
            :class:`.ConnectRepositoryGitProviderData` or as a dictionary.
        :param provider_id: The provider from which you want to connect the
            repo.
        :param token_id: The id of the token used for authentication.
        :param repository_id: The id of the repo to connect.
        :param is_test_student: Is this webhook for the test student?
        :param author_id: The id of the user for which we should get the
            webhook settings.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A job that will be started to connect and clone the
                  repository.
        """

        url = "/api/v1/git_providers/{providerId}/tokens/{tokenId}/repositories/{repositoryId}/connect".format(
            providerId=provider_id,
            tokenId=token_id,
            repositoryId=repository_id,
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "is_test_student": utils.to_dict(is_test_student),
            "author_id": utils.to_dict(author_id),
        }

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

    def get_all_repositories(
        self: "GitProviderService[codegrade.client.AuthenticatedClient]",
        *,
        provider_id: "str",
        token_id: "str",
        after: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "GitRepositoriesPage":
        """Get all repositories for the given git provider.

        :param provider_id: The provider from which you want to retrieve repos.
        :param token_id: The token to use to retrieve the repos.
        :param after: If given results after this cursor will be retrieved.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The token.
        """

        url = (
            "/api/v1/git_providers/{providerId}/tokens/{tokenId}/repositories/"
            .format(providerId=provider_id, tokenId=token_id)
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, after)).if_just(
            lambda val: params.__setitem__("after", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.git_repositories_page import GitRepositoriesPage

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(GitRepositoriesPage)
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

    def create_repository(
        self: "GitProviderService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateRepositoryGitProviderData"],
        *,
        provider_id: "str",
        token_id: "str",
        is_test_student: "bool",
        author_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Job":
        """Create a new repository and connect it to an assignment.

        :param json_body: The body of the request. See
            :class:`.CreateRepositoryGitProviderData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateRepositoryGitProviderData` or as a dictionary.
        :param provider_id: The provider in which you want to create a new
            repo.
        :param token_id: The id of the token used for authentication.
        :param is_test_student: Is this webhook for the test student?
        :param author_id: The id of the user for which we should get the
            webhook settings.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A job that will be started to connect and clone the
                  repository.
        """

        url = (
            "/api/v1/git_providers/{providerId}/tokens/{tokenId}/repositories/"
            .format(providerId=provider_id, tokenId=token_id)
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "is_test_student": utils.to_dict(is_test_student),
            "author_id": utils.to_dict(author_id),
        }

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
