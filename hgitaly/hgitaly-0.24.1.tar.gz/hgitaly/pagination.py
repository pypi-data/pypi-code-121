# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
NO_LIMIT = 2147483647


def extract_limit(request, field_name='pagination_params') -> int:
    """Extract limit with our conventions from given pagination_params.
    For context, gRPC does not have any notion of ``None``: absence
    of value is conflated with default value (which is 0 for integers).

    For specification, see comment in `shared.proto`.
    """
    if not request.HasField(field_name):
        return NO_LIMIT

    limit = getattr(request, field_name).limit
    # 0 really means to ask for empty response (it could have meant no
    # limit, the usual dilemma with integers in a language without None,
    # such as ProtoBuf)
    if limit < 0:
        limit = NO_LIMIT
    return limit
