#!/usr/bin/env python3

"""
Signature/digest calculation support.

--------

Copyright (C) 2011, 2012, 2013 Ian Donaldson <ian.donaldson@biotek.uio.no>
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

import base64
import hashlib
import re

strip_regexp = re.compile("[^A-Z0-9]")


def fix_signatures(signatures):

    "Remove prefixes from the given 'signatures'."

    fixed = []
    for signature in signatures:
        if not signature:
            return None
        parts = signature.split(":")
        if len(parts) > 1:
            signature = parts[1]
        fixed.append(signature)
    return fixed


def combine_signatures(signatures, legacy=0):

    """
    Combine the given 'signatures', sorting and digesting them. If the optional
    'legacy' parameter is set to a true value, the signatures will be converted
    to upper case and have non-alphanumeric characters removed.
    """

    signatures.sort()
    return make_signature("".join(signatures), legacy)


def normalise_sequence(sequence):

    """
    Normalise the given protein 'sequence' to be a continuous upper case string
    with no spaces or other non-alphanumeric characters.
    """

    return strip_regexp.sub("", sequence.upper())


def make_signature(sequence, legacy=0):

    """
    Make a signature from the given 'sequence' (which may actually be a
    combination of signatures as opposed to a protein sequence). If the optional
    'legacy' parameter is set to a true value, the signatures will be converted
    to upper case and have non-alphanumeric characters removed.
    """

    if legacy:
        sequence = normalise_sequence(sequence)
    digest = hashlib.sha1(sequence.encode("utf-8")).digest()
    b64enc = base64.b64encode(digest)[:-1]
    return b64enc.decode("utf-8")


def process_file(f, out, column, separator=",", append=0, append_length=0, legacy=0):

    """

    Process the file accessed via the object 'f', writing output to the 'out'
    stream combining signatures or sequence data from the given 'column' where
    each signature or data item is delimited by the given 'separator'.

    If 'append' is set to a true value, the resulting signatures will be
    appended to the columns. Otherwise, the selected columns will be replaced by
    the results.

    If 'append_length' is set to a true value, the signature lengths will be
    appended to the columns.

    Sequences or signatures will be converted to upper case, stripping
    non-alphanumeric characters, if the optional 'legacy' parameter is set to a
    true value. This is not recommended.
    """

    for line in f:
        columns = line.rstrip("\n").split("\t")
        inputs = columns[column].split(separator)
        signatures = fix_signatures(inputs)

        if signatures:
            result = combine_signatures(signatures, legacy)
            if append:
                columns.append(result)
            else:
                columns[column] = result
            if append_length:
                columns.append(str(sum(map(len, signatures))))
        else:
            columns.append("")

        out.write("\t".join(columns) + "\n")


# vim: tabstop=4 expandtab shiftwidth=4
