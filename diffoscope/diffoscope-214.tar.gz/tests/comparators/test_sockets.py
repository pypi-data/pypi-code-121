#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2020 Chris Lamb <lamby@debian.org>
# Copyright © 2021 Brent Spillner <s p i l l n e r @ a c m . o r g>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import os
import socket
import pytest

from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.socket_or_fifo import SocketOrFIFO, format_socket
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import get_data, load_fixture

sample_textfile = "text_ascii1"
sampletext = load_fixture(sample_textfile)


def make_socket(path):
    if os.path.exists(path):
        os.remove(path)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(path)
    return specialize(FilesystemFile(path))


def make_pipe(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)
    return specialize(FilesystemFile(path))


@pytest.fixture
def endpoints(tmpdir):
    def makename(tag):
        return os.path.join(tmpdir, "test_" + tag)

    test_points = zip(
        [make_socket, make_socket, make_pipe, make_pipe],
        map(makename, ["socket1", "socket2", "pipe1", "pipe2"]),
    )
    yield [(name, f(name)) for (f, name) in test_points]
    for (_, name) in test_points:
        os.remove(name)


@pytest.fixture
def expected_results(endpoints):
    descriptions = [
        format_socket(obj.get_type(), path) for (path, obj) in endpoints
    ]
    [sock1_desc, sock2_desc, pipe1_desc, pipe2_desc] = descriptions

    # Prefix every line of the sample text file with '+' to predict RHS of the diff
    sampletext_contents = get_data(sample_textfile)
    sample_lines = sampletext_contents.count("\n")
    added_text = "+" + "\n+".join(sampletext_contents.split("\n")[:-1]) + "\n"

    sock_text_diff = (
        "@@ -1 +1,{} @@\n".format(sample_lines) + "-" + sock1_desc + added_text
    )
    pipe_text_diff = (
        "@@ -1 +1,{} @@\n".format(sample_lines) + "-" + pipe1_desc + added_text
    )
    sock_sock_diff = "@@ -1 +1 @@\n" + "-" + sock1_desc + "+" + sock2_desc
    pipe_pipe_diff = "@@ -1 +1 @@\n" + "-" + pipe1_desc + "+" + pipe2_desc
    sock_pipe_diff = "@@ -1 +1 @@\n" + "-" + sock1_desc + "+" + pipe1_desc
    pipe_sock_diff = "@@ -1 +1 @@\n" + "-" + pipe1_desc + "+" + sock1_desc
    yield (
        sock_text_diff,
        pipe_text_diff,
        sock_sock_diff,
        pipe_pipe_diff,
        sock_pipe_diff,
        pipe_sock_diff,
    )


def test_sockets(endpoints, expected_results, sampletext):
    (names, objects) = zip(*endpoints)
    (sock1, sock2, pipe1, pipe2) = objects
    (
        sock_text_diff,
        pipe_text_diff,
        sock_sock_diff,
        pipe_pipe_diff,
        sock_pipe_diff,
        pipe_sock_diff,
    ) = expected_results

    assert isinstance(sock1, SocketOrFIFO)
    assert isinstance(pipe1, SocketOrFIFO)

    assert sock1.compare(sampletext).unified_diff == sock_text_diff
    assert pipe1.compare(sampletext).unified_diff == pipe_text_diff

    assert sock1.compare(sock1) == None
    assert pipe1.compare(pipe1) == None
    assert sock1.compare(sock2).unified_diff == sock_sock_diff
    assert pipe1.compare(pipe2).unified_diff == pipe_pipe_diff
    assert sock1.compare(pipe1).unified_diff == sock_pipe_diff
    assert pipe1.compare(sock1).unified_diff == pipe_sock_diff
