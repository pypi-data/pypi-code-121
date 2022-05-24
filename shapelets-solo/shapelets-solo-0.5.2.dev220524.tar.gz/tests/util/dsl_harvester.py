# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

"""
Once you have run the integration tests, dsl_op.py will contain
the full list of available functions, plus dsl implementation.
This script takes the content and removes the implementation,
replacing it by 'pass', so that pylint can have the headers and
not complaint.
"""

import os
import sys
from enum import Enum
from pathlib import Path


class State(Enum):
    LOOK_FOR_DEF = 0
    IN_DEF = 1


if __name__ == "__main__":
    cwd = Path.cwd()
    in_file_path = cwd / '..' / '..' / 'shapelets' / 'dsl' / 'dsl_op.py'
    out_file_path = in_file_path / '..' / 'dsl_op.py'
    with open(in_file_path, 'r') as src_file:
        state = State.LOOK_FOR_DEF
        QUOTE_COUNT = 0
        with open(out_file_path, 'w') as dst_file:
            for in_line in src_file:
                if state == State.LOOK_FOR_DEF:
                    if in_line.startswith('def'):
                        state = State.IN_DEF
                        QUOTE_COUNT = 0
                    elif QUOTE_COUNT == 2:
                        continue
                elif state == State.IN_DEF:
                    if '"""' in in_line:
                        QUOTE_COUNT += 1
                    elif QUOTE_COUNT == 2:
                        dst_file.write(f"    pass{os.linesep}")
                        state = State.LOOK_FOR_DEF
                        continue
                else:
                    sys.exit(f"unknown state: {state}")
                dst_file.write(in_line)
