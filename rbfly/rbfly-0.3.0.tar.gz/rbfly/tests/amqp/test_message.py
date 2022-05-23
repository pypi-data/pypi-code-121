#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from rbfly.amqp._message import MessageCtx, encode_amqp, decode_amqp
from rbfly.error import AMQPDecoderError

import pytest

# decoding and encoding of AMQP types in the context of Python objects
DATA = (
    # binary, opaque message (first with nulls in the message)
    (MessageCtx(b'\x01\x00\x00\x00\x02'), b'\x00Su\xa0\x05\x01\x00\x00\x00\x02'),
    (MessageCtx(b'abcde'), b'\x00Su\xa0\x05abcde'),
    (MessageCtx(b'a' * 256), b'\x00Su\xb0\x00\x00\x01\x00' + b'a' * 256),

    # string
    (MessageCtx('abcde'), b'\x00Sw\xa1\x05abcde'),
    (MessageCtx('a' * 256), b'\x00Sw\xb1\x00\x00\x01\x00' + b'a' * 256),

    # boolean
    (MessageCtx(True), b'\x00SwA'),
    (MessageCtx(False), b'\x00SwB'),

    # int
    (MessageCtx(-2 ** 31), b'\x00Sw\x71\x80\x00\x00\x00'),
    (MessageCtx(2 ** 31 - 1), b'\x00Sw\x71\x7f\xff\xff\xff'),

    # long
    (MessageCtx(-2 ** 63), b'\x00Sw\x81\x80\x00\x00\x00\x00\x00\x00\x00'),
    (MessageCtx(2 ** 63 - 1), b'\x00Sw\x81\x7f\xff\xff\xff\xff\xff\xff\xff'),

    # ulong
    (MessageCtx(2 ** 64 - 1), b'\x00Sw\x80\xff\xff\xff\xff\xff\xff\xff\xff'),

    # double
    (MessageCtx(201.102), b'\x00Sw\x82@i#C\x95\x81\x06%'),

    # map
    (
        MessageCtx({'a': 1, 'b': 2}),
        b'\x00Sw\xd1\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # nested map
    (
        MessageCtx({'a': 1, 'b': {'a': 1, 'b': 2}}),  # type: ignore
        b'\x00Sw\xd1\x00\x00\x00\x24\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\xd1\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # list
    (
        MessageCtx(['a', 1, 'b', 2]),
        b'\x00Sw\xd0\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # nested list
    (
        MessageCtx(['a', 1, 'b', ['a', 1, 'b', 2]]),  # type: ignore
        b'\x00Sw\xd0\x00\x00\x00\x24\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\xd0\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
)

# decoding of AMQP types, which are not encoded by rbfly
DATA_PARSED = (
    # ubyte
    (MessageCtx(255), b'\x00Sw\x50\xff'),

    # ushort
    (MessageCtx(2 ** 16 - 1), b'\x00Sw\x60\xff\xff'),

    # uint, smalluint, uint0
    (MessageCtx(2 ** 32 - 1), b'\x00Sw\x70\xff\xff\xff\xff'),
    (MessageCtx(255), b'\x00Sw\x52\xff'),
    (MessageCtx(0), b'\x00Sw\x43'),

    # ulong, smallulong, ulong0
    (MessageCtx(2 ** 64 - 1), b'\x00Sw\x80\xff\xff\xff\xff\xff\xff\xff\xff'),
    (MessageCtx(255), b'\x00Sw\x53\xff'),
    (MessageCtx(0), b'\x00Sw\x44'),

    # byte
    (MessageCtx(-1), b'\x00Sw\x51\xff'),

    # short
    (MessageCtx(-1), b'\x00Sw\x61\xff\xff'),

    # int, smallint
    (MessageCtx(-1), b'\x00Sw\x71\xff\xff\xff\xff'),
    (MessageCtx(-1), b'\x00Sw\x54\xff'),

    # long
    (MessageCtx(-1), b'\x00Sw\x81\xff\xff\xff\xff\xff\xff\xff\xff'),
    (MessageCtx(-1), b'\x00Sw\x55\xff'),

    # float
    (MessageCtx(201.1020050048828), b'\x00Sw\x72CI\x1a\x1d'),

    # map8
    (
        MessageCtx({'a': 1, 'b': 2}),
        b'\x00Sw\xc1\x10\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # list8
    (
        MessageCtx(['a', 1, 'b', 2]),
        b'\x00Sw\xc0\x10\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # list0
    (
        MessageCtx([]),
        b'\x00Sw\x45',
    ),
)

MESSAGE_REPR = (
    (
        MessageCtx('a-string'),
        'MessageCtx(body=\'a-string\', stream_offset=0, stream_timestamp=0.0)',
    ),
    (
        MessageCtx('a-string-and-more', stream_timestamp=2.0),
        'MessageCtx(body=\'a-string-a...\', stream_offset=0, stream_timestamp=2.0)',
    ),
    (
        MessageCtx(b'binary-data-and-more'),
        'MessageCtx(body=b\'binary-dat...\', stream_offset=0, stream_timestamp=0.0)',
    ),
    (
        MessageCtx(15),
        'MessageCtx(body=15, stream_offset=0, stream_timestamp=0.0)',
    ),
    (
        MessageCtx({'a': 15}),
        'MessageCtx(body={\'a\': 15}, stream_offset=0, stream_timestamp=0.0)',
    ),
)

DATA_INVALID = (
    # minimum 4 bytes expected
    b'\x00Sw',

    # uint32 missing one byte
    b'\x00Sw\x71\x80\x00\x00',

    # string/byte string: expected buffer size is one more byte
    b'\x00Sw\xa1\x06abcde',

    # size of compound (map) buffer: expected buffer size is one more byte
    b'\x00Sw\xd1\x00\x00\x00\x18\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00',

    # count of compound (map): odd number of elements (3 to be exact) instead of even
    b'\x00Sw\xd1\x00\x00\x00\x18\x00\x00\x00\x03\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
)

@pytest.mark.parametrize('message, expected', DATA)
def test_encode(message: MessageCtx, expected: bytes) -> None:
    """
    Test encoding AMQP messages.
    """
    msg_buffer = bytearray(1024)
    size = encode_amqp(msg_buffer, message)
    assert bytes(msg_buffer[:size]) == expected

def test_encode_binary_invalid() -> None:
    """
    Test error on encoding too long binary AMQP messages.
    """
    msg_buffer = bytearray(1024)
    with pytest.raises(ValueError):
        encode_amqp(msg_buffer, MessageCtx(b'a' * 2 ** 32))

@pytest.mark.parametrize('message, data', DATA + DATA_PARSED)
def test_decode(message: MessageCtx, data: bytes) -> None:
    """
    Test decoding AMQP messages.
    """
    result = decode_amqp(data)
    assert result == message

@pytest.mark.parametrize('message, expected', MESSAGE_REPR)
def test_message_repr(message: MessageCtx, expected: str) -> None:
    """
    Test AMQP message representation.
    """
    assert repr(message) == expected

@pytest.mark.parametrize('data', DATA_INVALID)
def test_decode_invalid_size(data: bytes) -> None:
    """
    Test decoding AMQP data when declared size and buffer do not agree.
    """
    with pytest.raises(AMQPDecoderError):
        decode_amqp(data)

# vim: sw=4:et:ai
