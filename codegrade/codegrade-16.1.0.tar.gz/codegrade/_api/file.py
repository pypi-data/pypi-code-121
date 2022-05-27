"""The endpoints for file objects.

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


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class FileService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def download(
        self,
        *,
        filename: "str",
        mime: Maybe["str"] = Nothing,
        as_attachment: "bool" = False,
        name: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "bytes":
        """Serve some specific file in the uploads folder.

        Warning: The file will be deleted after you download it!

        :param filename: The filename of the file to get.
        :param mime: The mime type header to set on the response.
        :param as_attachment: If truthy the response will have a
            `Content-Disposition: attachment` header set.
        :param name: The filename for the attachment, defaults to the second
            part of the url.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested file.
        """

        url = "/api/v1/files/{filename}".format(filename=filename)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "as_attachment": utils.to_dict(as_attachment),
        }
        maybe_from_nullable(t.cast(t.Any, mime)).if_just(
            lambda val: params.__setitem__("mime", val)
        )
        maybe_from_nullable(t.cast(t.Any, name)).if_just(
            lambda val: params.__setitem__("name", val)
        )

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
