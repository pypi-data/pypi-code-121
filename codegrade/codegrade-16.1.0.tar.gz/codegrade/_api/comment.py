"""The endpoints for comment objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.comment_reply_edit import CommentReplyEdit
    from ..models.create_comment_data import CreateCommentData
    from ..models.create_comment_reply_data import CreateCommentReplyData
    from ..models.deleted_comment_reply import DeletedCommentReply
    from ..models.extended_non_deleted_comment_reply import (
        ExtendedNonDeletedCommentReply,
    )
    from ..models.general_feedback_comment_base_with_extended_replies import (
        GeneralFeedbackCommentBaseWithExtendedReplies,
    )
    from ..models.inline_feedback_comment_base_with_extended_replies import (
        InlineFeedbackCommentBaseWithExtendedReplies,
    )
    from ..models.patch_comment_reply_data import PatchCommentReplyData


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class CommentService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def create_base(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateCommentData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[InlineFeedbackCommentBaseWithExtendedReplies, GeneralFeedbackCommentBaseWithExtendedReplies]":
        """Create a new comment base, or retrieve an existing one.

        :param json_body: The body of the request. See
            :class:`.CreateCommentData` for information about the possible
            fields. You can provide this data as a :class:`.CreateCommentData`
            or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just created comment base.
        """

        url = "/api/v1/comments/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.general_feedback_comment_base_with_extended_replies import (
                GeneralFeedbackCommentBaseWithExtendedReplies,
            )
            from ..models.inline_feedback_comment_base_with_extended_replies import (
                InlineFeedbackCommentBaseWithExtendedReplies,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(
                        InlineFeedbackCommentBaseWithExtendedReplies
                    ),
                    parsers.ParserFor.make(
                        GeneralFeedbackCommentBaseWithExtendedReplies
                    ),
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

    def create_reply(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateCommentReplyData"],
        *,
        comment_base_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]":
        """Add a reply to a comment base.

        :param json_body: The body of the request. See
            :class:`.CreateCommentReplyData` for information about the possible
            fields. You can provide this data as a
            :class:`.CreateCommentReplyData` or as a dictionary.
        :param comment_base_id: The id of the base to which you want to add a
            reply.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just created reply.
        """

        url = "/api/v1/comments/{commentBaseId}/replies/".format(
            commentBaseId=comment_base_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.deleted_comment_reply import DeletedCommentReply
            from ..models.extended_non_deleted_comment_reply import (
                ExtendedNonDeletedCommentReply,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedNonDeletedCommentReply),
                    parsers.ParserFor.make(DeletedCommentReply),
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

    def delete_reply(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        *,
        comment_base_id: "int",
        reply_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete the given reply.

        :param comment_base_id: The base of the given reply.
        :param reply_id: The id of the reply to delete.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/comments/{commentBaseId}/replies/{replyId}".format(
            commentBaseId=comment_base_id, replyId=reply_id
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

    def patch_reply(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchCommentReplyData"],
        *,
        comment_base_id: "int",
        reply_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]":
        """Update the content of a reply.

        :param json_body: The body of the request. See
            :class:`.PatchCommentReplyData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchCommentReplyData` or as a dictionary.
        :param comment_base_id: The base of the given reply.
        :param reply_id: The id of the reply for which you want to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just updated reply.
        """

        url = "/api/v1/comments/{commentBaseId}/replies/{replyId}".format(
            commentBaseId=comment_base_id, replyId=reply_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.deleted_comment_reply import DeletedCommentReply
            from ..models.extended_non_deleted_comment_reply import (
                ExtendedNonDeletedCommentReply,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedNonDeletedCommentReply),
                    parsers.ParserFor.make(DeletedCommentReply),
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

    def get_all_reply_edits(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        *,
        comment_base_id: "int",
        reply_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[CommentReplyEdit]":
        """Get the edits of a reply.

        :param comment_base_id: The base of the given reply.
        :param reply_id: The id of the reply for which you want to get the
            edits.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of edits, sorted from newest to oldest.
        """

        url = (
            "/api/v1/comments/{commentBaseId}/replies/{replyId}/edits/".format(
                commentBaseId=comment_base_id, replyId=reply_id
            )
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.comment_reply_edit import CommentReplyEdit

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(CommentReplyEdit))
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

    def approve_reply(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        *,
        comment_base_id: "int",
        reply_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]":
        """Update the approval status of a reply.

        :param comment_base_id: The base of the given reply.
        :param reply_id: The id of the reply for which you want to update the
            approval.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just updated reply.
        """

        url = (
            "/api/v1/comments/{commentBaseId}/replies/{replyId}/approval"
            .format(commentBaseId=comment_base_id, replyId=reply_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.deleted_comment_reply import DeletedCommentReply
            from ..models.extended_non_deleted_comment_reply import (
                ExtendedNonDeletedCommentReply,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedNonDeletedCommentReply),
                    parsers.ParserFor.make(DeletedCommentReply),
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

    def disapprove_reply(
        self: "CommentService[codegrade.client.AuthenticatedClient]",
        *,
        comment_base_id: "int",
        reply_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]":
        """Update the approval status of a reply.

        :param comment_base_id: The base of the given reply.
        :param reply_id: The id of the reply for which you want to update the
            approval.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just updated reply.
        """

        url = (
            "/api/v1/comments/{commentBaseId}/replies/{replyId}/approval"
            .format(commentBaseId=comment_base_id, replyId=reply_id)
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.deleted_comment_reply import DeletedCommentReply
            from ..models.extended_non_deleted_comment_reply import (
                ExtendedNonDeletedCommentReply,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedNonDeletedCommentReply),
                    parsers.ParserFor.make(DeletedCommentReply),
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
