# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import pytest

from .. import stream


def test_aggregate_flush_batch():
    in_data = iter([b'AAA', b'BB', b'B', b'C'])
    max_size = 2
    data = stream.aggregate_flush_batch(in_data, len, max_size)
    data = list(data)
    assert data == [[b'AAA'], [b'BB', b'B'], [b'C']]


def test_concat_resplit():
    in_data = iter([b'AAB', b'BCCDD'])
    max_size = 2
    data = stream.concat_resplit(in_data, max_size)
    data = list(data)
    assert data == [b'AA', b'BB', b'CC', b'DD']


def test_env_write_buffer_size(monkeypatch):
    monkeypatch.setitem(os.environ, 'GITALY_STREAMIO_WRITE_BUFFER_SIZE', '12')

    assert stream.env_write_buffer_size() == 12


def test_iter_boolean_lookahead():
    in_data = iter([b'AAB', b'BCCDD'])
    max_size = 2
    itr = stream.concat_resplit(in_data, max_size)
    batched_data = stream.iter_boolean_lookahead(itr)
    for _ in range(3):
        data, eop = next(batched_data)
        assert len(data) == 2
        assert not eop
    data, eop = next(batched_data)
    assert len(data) == 2
    assert eop
    # with empty iterator
    with pytest.raises(StopIteration):
        data = stream.iter_boolean_lookahead(iter([]))
        next(data)


def test_split_batches():
    in_data = b'AABBCCDD'
    max_size = 2
    data = stream.split_batches(in_data, max_size)
    data = list(data)
    assert data == [b'AA', b'BB', b'CC', b'DD']
