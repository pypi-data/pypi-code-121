#!/usr/bin/env python3

"""
Very limited support for Java object serialisation.

This functionality is only needed for iRefScape export, which for some reason
uses this representation instead of a plain text representation. Although a
general serialiser could be used, the output of previous data files was
deconstructed instead and the immutable sections from such files are reproduced
here.

--------

Copyright (C) 2012 Ian Donaldson <ian.donaldson@biotek.uio.no>
Original author: Paul Boddie <paul.boddie@biotek.uio.no>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct

# Magic number and protocol version.
# Outer array description.
# Inner array description.

stream_start = (
    "\xac\xed\x00\x05"
    "\x75\x72\x00\x03[[I\x17\xf7\xe4\x4f\x19\x8f\x89\x3c\x02\x00\x00\x78\x70\x00\x16\xc9\x3d"
    "\x75\x72\x00\x02[I\x4d\xba\x60\x26\x76\xea\xb2\xa5\x02\x00\x00\x78\x70"
)

first_pair_value_start = "\x00\x00\x00\x02"
pair_value_start = "\x75\x71\x00\x7e\x00\x02" + first_pair_value_start


def dump_pairs(pairs, out):
    out.write(stream_start)
    first = 1
    for pair in pairs:
        if first:
            first = 0
            out.write(first_pair_value_start)
        else:
            out.write(pair_value_start)
        out.write(struct.pack(">l", pair[0]))
        out.write(struct.pack(">l", pair[1]))


# vim: tabstop=4 expandtab shiftwidth=4
