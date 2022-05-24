# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
import uuid


def unique_id_str() -> str:
    return str(uuid.uuid1())


def unique_id_int() -> int:
    return uuid.uuid1().int
