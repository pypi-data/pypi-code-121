# Copyright 2020 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial.node import (
    hex,
)

from heptapod.gitlab.tag import (
    gitlab_tag_ref,
)

EXCLUDED_TAG_TYPES = (b'local', None)  # 'tip' has type None


def iter_gitlab_tags(repo, deref=True):
    """Iterate on the tags that are visible to GitLab.

    Yield tag name and tag target

    :param bool deref: if ``True``, targets are :class:`changectx`, else
    hexadecimal node ids, as :class:`str`.
    """
    for name, node in repo.tags().items():
        if repo.tagtype(name) in EXCLUDED_TAG_TYPES:
            continue

        yield name, (repo[node] if deref else hex(node).decode('ascii'))


def iter_gitlab_tags_as_refs(repo, **kwargs):
    """Iterate on the repo tags, yielding full Git refs and change contexts.

    """
    for name, target in iter_gitlab_tags(repo, **kwargs):
        yield gitlab_tag_ref(name), target
