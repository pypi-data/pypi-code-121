# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import random

from heptapod.testhelpers import LocalRepoWrapper

from ..stub.shared_pb2 import Repository

MINIMAL_HG_CONFIG = dict(extensions=dict(topic='', evolve=''))


def make_empty_repo(storages_root, relative_path=None, storage='default',
                    extra_extensions=()):
    """Create an empty repo, ready for most of HGitaly tests.

    :relative_path: path to the repo, relative to server_repos_root, and
                    hence also relative path in the sense of Gitaly protocol.
                    Can be given as :class:`str` or :class:`pathlib.Path`.
                    If ``None``, a path is randomly chosen.
    :storage: name of the target storage, will have to be created and
              registered before hand on the testing grpc server if needed.

    The path to the repository root can be retrieved from the returned
    wrapper as the :class:`pathlib.Path` instance `path` attribute.

    return: wrapper, gRPC Repository message
    """
    if relative_path is None:
        relative_path = 'repo-' + hex(random.getrandbits(64))[2:]
    repo_path = storages_root / storage / relative_path
    config = MINIMAL_HG_CONFIG
    config['extensions'].update((ext, '') for ext in extra_extensions)
    wrapper = LocalRepoWrapper.init(repo_path, config=config)
    wrapper.write_hgrc(config)

    grpc_repo = Repository(relative_path=str(relative_path),
                           storage_name=storage)
    return wrapper, grpc_repo


def make_tree_shaped_repo(storages_root, **kw):
    """Make a testing repo with a tree shape.

    :return: ``(wrapper, grpc_repo, changesets)``, where ``wrapper`` and
             ``grpc_repo`` are as in :func:`make_empy_repo` and ``changesets``
             is a :class:`dict` whose values are interesting changesets,
             given as :class:`changectx instances`

    Here's the graphlog, with added annotation for keys of the ``changesets``
    :class:`dict`::

      $ hg log -G -T '{desc}\nbranch & topic: {branch}:{topic}\n\n'
      @  Topic head  KEY: top2
      |  branch & topic: default:zzetop
      |
      o  Topic first  KEY: top1
      |  branch & topic: default:zzetop
      |
      | o  Other main wild head  KEY: wild2
      | |  branch & topic: other:
      | |
      | | o  Other wild  KEY: wild1
      | |/   branch & topic: other:
      | |
      | o  Start other  KEY: other_base
      |/   branch & topic: other:
      |
      | o  Head of default  KEY: default
      |/   branch & topic: default:
      |
      o  Base  KEY: base
         branch & topic: default:
    """
    wrapper, grpc_repo = make_empty_repo(storages_root, **kw)
    chgs = {}
    base = chgs['base'] = wrapper.write_commit('foo', message='Base')
    chgs['default'] = wrapper.write_commit('foo', message='Head of default')
    other_base = chgs['other_base'] = wrapper.write_commit(
        'foo', message='Start other', branch='other', parent=base)
    chgs['wild1'] = wrapper.write_commit('foo', message='Other wild',
                                         branch='other')
    chgs['wild2'] = wrapper.write_commit('foo', message='Other main wild head',
                                         branch='other', parent=other_base)
    chgs['top1'] = wrapper.write_commit('foo', message='Topic first',
                                        branch='default', topic='zzetop',
                                        parent=base)
    chgs['top2'] = wrapper.write_commit('foo', message='Topic head')
    return wrapper, grpc_repo, chgs
