# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import os
import pytest

from mercurial import (
    phases,
)
from hgext3rd.heptapod.branch import (
    write_gitlab_branches,
)


from hgitaly.testing.ssh import hg_exe_path
from hgitaly.testing.sshd import hg_ssh_setup
from hgitaly.tests.common import make_empty_repo

from hgitaly.stub.mercurial_repository_pb2 import (
    ConfigItemType,
    GetConfigItemRequest,
    MercurialPeer,
    PushRequest,
)
from hgitaly.stub.mercurial_repository_pb2_grpc import (
    MercurialRepositoryServiceStub,
)

parametrize = pytest.mark.parametrize


def test_config_item(grpc_channel, server_repos_root):
    hg_repo_stub = MercurialRepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def rpc_config_bool(section, name):
        return hg_repo_stub.GetConfigItem(
            GetConfigItemRequest(repository=grpc_repo,
                                 section=section,
                                 name=name,
                                 as_type=ConfigItemType.BOOL)
        ).as_bool

    # Relying on current defaults in some random core settings, just pick
    # some other ones if they change.
    assert rpc_config_bool('format', 'usestore') is True
    assert rpc_config_bool('commands', 'status.verbose') is False


@pytest.fixture
def push_fixture(grpc_channel, server_repos_root):
    hg_repo_stub = MercurialRepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    target_wrapper, _target_grpc_repo = make_empty_repo(server_repos_root)

    def push(remote_url=target_wrapper.path, peer_opts=None, **kw):
        if peer_opts is None:
            peer_opts = {}
        return hg_repo_stub.Push(PushRequest(
            repository=grpc_repo,
            remote_peer=MercurialPeer(url=str(remote_url), **peer_opts),
            **kw))
    yield wrapper, target_wrapper, push


def set_auto_publishing(repo_wrapper, publish):
    """Tweak persistently the auto-publishing behaviour of the repository

    In a typical push, the repository configuration will be initialized
    independently from the objects of these tests, so this has to be done
    in the `hgrc` file.

    TODO consider for inclusion in mercurial-testhelpers.
    """
    (repo_wrapper.path / '.hg/hgrc').write_text(
        '[phases]\n'
        'publish=%s\n' % ('yes' if publish else 'no')
        )


def test_bare_push(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    def get_nodes_ids(repo):
        return {repo[r].hex() for r in repo.revs("all()")}

    ctx_pub = wrapper.commit_file('foo')
    wrapper.set_phase("public", [ctx_pub.hex()])
    ctx_draft = wrapper.commit_file('foo')

    # pushing public changesets only
    res = push()
    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_nodes_ids(target_wrapper.repo)
    assert target_node_ids == {ctx_pub.hex()}

    # idempotency
    res = push()
    assert not res.new_changesets

    # pushing drafts explicitely
    # this needs us to make the target repo non-publishing
    set_auto_publishing(target_wrapper, False)
    res = push(include_drafts=True)
    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_nodes_ids(target_wrapper.repo)
    assert target_node_ids == {ctx_pub.hex(), ctx_draft.hex()}

    # idempotency for drafts
    res = push(include_drafts=True)
    assert not res.new_changesets

    # case of target not existing
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=target_wrapper.path / 'does/not/exist')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "could not be used as a peer" in exc_info.value.details()

    # case of push failing on target (other ways to make it fail would
    # be of course admissible)
    (target_wrapper.path / '.hg' / 'hgrc').write_text(
        "[experimental]\n"
        "single-head-per-branch=yes\n")
    wrapper.write_commit('bar', parent=ctx_pub)
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=target_wrapper.path, include_drafts=True)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL


def test_push_branch(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    def get_node_ids(wrapper, revset="all()"):
        repo = wrapper.repo
        return {repo[r].hex() for r in repo.revs(revset)}

    ctx_foo = wrapper.commit_file('foo')
    wrapper.commit_file('baz')
    wrapper.update(0)
    ctx_bar = wrapper.commit_file('bar', branch="stable")
    wrapper.set_phase("public", [ctx_bar.hex()])
    expected_node_ids = {ctx_foo.hex(), ctx_bar.hex()}
    res = push(only_gitlab_branches_matching=[b'branch/stable'])

    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_node_ids(target_wrapper)
    assert target_node_ids == expected_node_ids

    # a head draft is not pushed, but its public ancestors are
    # (also using a wildcard pattern)
    ctx_bar2 = wrapper.commit_file('bar', branch='stable')
    ctx_bar3 = wrapper.commit_file('bar', branch='stable')
    wrapper.set_phase('public', [ctx_bar2.hex()])
    res = push(only_gitlab_branches_matching=[b'branch/st*'])
    assert res.new_changesets
    target_wrapper.reload()
    assert get_node_ids(target_wrapper, revset="stable") == {ctx_bar2.hex()}

    # pushing drafts explicitely
    # auto-publication is prohibited for now
    set_auto_publishing(target_wrapper, False)
    res = push(only_gitlab_branches_matching=[b'branch/stable'],
               include_drafts=True)
    assert res.new_changesets
    target_wrapper.reload()
    assert get_node_ids(target_wrapper, revset="stable") == {ctx_bar3.hex()}

    # pushing a branch that doesn't exist currently is not an error
    # (it can happen temporarily and still be the intent in repeated
    # invocations, such as mirrorring, the primary use-case)
    assert not push(only_gitlab_branches_matching=[b'z*']).new_changesets


@pytest.fixture
def ssh_fixture(tmpdir):
    working_dir = tmpdir / 'sshd'
    working_dir.mkdir()
    yield from hg_ssh_setup(working_dir)


def test_push_ssh(push_fixture, ssh_fixture):
    wrapper, target_wrapper, push = push_fixture
    server, client_key, known_hosts = ssh_fixture

    ctx = wrapper.commit_file('foo')

    # auto-publication is prohibited for now
    set_auto_publishing(target_wrapper, False)
    res = push(
        include_drafts=True,
        remote_url=f'ssh://{server.host}:{server.port}/{target_wrapper.path}',
        peer_opts=dict(
            ssh_remote_command=os.fsencode(hg_exe_path()),
            ssh_key=client_key,
            ssh_known_hosts=known_hosts,
        ))

    assert res.new_changesets

    target_wrapper.reload()
    assert ctx in target_wrapper.repo


def test_push_auto_publishing_error(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    ctx = wrapper.commit_file('foo')
    assert ctx.phase() == phases.draft  # making sure of main hypothesis

    set_auto_publishing(target_wrapper, True)

    with pytest.raises(grpc.RpcError) as exc_info:
        push(include_drafts=True)
    # debatable, but we currently don't have a clear way to tell the
    # inner exception apart
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'push would publish' in exc_info.value.details()


def test_push_unexpected_error(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    # we don't have many ways to trigger internal errors when
    # monkeypatch can't work (server is not in the same process):
    # let's corrupt the repo.

    write_gitlab_branches(wrapper.repo, {b'wrecked': b'not-a-hash'})

    with pytest.raises(grpc.RpcError) as exc_info:
        push(only_gitlab_branches_matching=[b'wrecked'])

    # debatable, but we currently don't have a clear way to tell the
    # inner exception apart
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    details = exc_info.value.details()
    assert "Unexpected" in details
    assert 'not-a-hash' in details


@parametrize('url', (
    'http://.heptapod.test/a/repo',  # hg.peer() fails at IDNA decoding
    'http://\u2100.test',  # refused for NKFC normalisation by urlparse()
    'mailto:pushoversmtpisajoke@heptapod.test',  # wrong scheme
    '/tmp/not_in_storage',
))
def test_push_invalid_url(push_fixture, url):
    _wrapper, _target_wrapper, push = push_fixture
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=url)
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
