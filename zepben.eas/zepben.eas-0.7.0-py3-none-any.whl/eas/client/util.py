#  Copyright 2020 Zeppelin Bend Pty Ltd
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["construct_url"]

from typing import Union


def construct_url(protocol, host, path, port: Union[str, int] = None) -> str:
    return f"{protocol}://{host}{f':{port}' if port else ''}{path}"
