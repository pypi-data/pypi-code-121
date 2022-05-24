# coding: utf-8
# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

import os

from mercurial import (
    exchange,
    pycompat,
)

from ..branch import iter_gitlab_branches_matching
from ..peer import (
    FileURLOutsidePath,
    InvalidURLScheme,
    PeerInitException,
    URLParseError,
    hg_remote_peer,
)

from ..errors import (
    internal_error,
    invalid_argument,
    not_implemented,
)
from ..stub.mercurial_repository_pb2 import (
    ConfigItemType,
    GetConfigItemRequest,
    GetConfigItemResponse,
    PushRequest,
    PushResponse,
)
from ..stub.mercurial_repository_pb2_grpc import (
    MercurialRepositoryServiceServicer,
)
from ..servicer import HGitalyServicer

logger = logging.getLogger(__name__)


class MercurialRepositoryServicer(MercurialRepositoryServiceServicer,
                                  HGitalyServicer):
    """MercurialRepositoryService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def GetConfigItem(self,
                      request: GetConfigItemRequest,
                      context) -> GetConfigItemResponse:
        repo = self.load_repo(request.repository, context)
        section = pycompat.sysbytes(request.section)
        name = pycompat.sysbytes(request.name)

        if request.as_type == ConfigItemType.BOOL:
            # TODO error treatment if value is not boolean
            return GetConfigItemResponse(
                as_bool=repo.ui.configbool(section, name))

        return not_implemented(  # pragma no cover
            context, GetConfigItemResponse,
            issue=60)

    def Push(self, request: PushRequest, context) -> PushResponse:
        repo = self.load_repo(request.repository, context)
        repo.ui.setconfig(b'hooks', b'pretxnclose.heptapod_sync', b'')
        repo.ui.setconfig(b'experimental', b'auto-publish', b'abort')

        remote_url = request.remote_peer.url

        # storage name has already been validated by the repository resolution
        storage_path = os.fsdecode(
            self.storages.get(request.repository.storage_name))

        try:
            with hg_remote_peer(repo, request.remote_peer,
                                storage_path=storage_path) as remote_peer:
                include_drafts = request.include_drafts
                only_revs = None
                only_branches_matching = request.only_gitlab_branches_matching
                if only_branches_matching:
                    only_heads = [
                        ctx.hex()
                        for _name, ctx in iter_gitlab_branches_matching(
                            repo, only_branches_matching)
                    ]
                    if include_drafts:
                        only_revs = repo.revs('%ls', only_heads)
                    else:
                        # Note that this is public ancestors of the given
                        # heads,  not the same as ancestors of public heads.
                        # This form is preferred because it doesn't block the
                        # push of the protected branch if its head happens
                        # to be a draft.
                        only_revs = repo.revs('public() and ::(%ls)',
                                              only_heads)
                elif not include_drafts:
                    only_revs = repo.revs('public()')

                if only_revs is not None and not only_revs:
                    return PushResponse(new_changesets=False)

                push_kwargs = dict(newbranch=True)
                if only_revs is not None:
                    push_kwargs['revs'] = [repo[rev].node()
                                           for rev in only_revs]

                try:
                    pushop = exchange.push(repo=repo, remote=remote_peer,
                                           **push_kwargs)
                except Exception as exc:
                    return internal_error(
                        context, PushResponse,
                        "Error pushing to %r: %s" % (remote_url, exc))

                new_changesets = (pushop.cgresult != 0
                                  and pushop.cgresult is not None)
                return PushResponse(new_changesets=new_changesets)
        except URLParseError as exc:
            return invalid_argument(
                context, PushResponse,
                "Invalid URL %r for push: %s " % exc.args)
        except InvalidURLScheme as exc:
            return invalid_argument(
                context, PushResponse,
                "Invalid scheme %r for push URL %r. Please use one of %r" % (
                    exc.args[0], remote_url, exc.args[1]))
        except FileURLOutsidePath as exc:
            return invalid_argument(
                context, PushResponse,
                "file URL %r not under storage %r root directory" % exc.args)
        except PeerInitException as exc:
            return invalid_argument(
                context, PushResponse,
                "URL %r could not be used as a peer for push: %s" % (
                    remote_url, exc))
        except Exception as exc:
            return internal_error(
                context, PushResponse,
                "Unexpected error, not in the actual push to %r: %s" % (
                    remote_url, exc))
