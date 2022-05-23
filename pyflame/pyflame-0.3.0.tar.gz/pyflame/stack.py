# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license


def pack_stack(frame):
    try:
        stack = None
        while frame is not None:
            code = frame.f_code
            stack = (
                code.co_name,
                code.co_filename,
                code.co_firstlineno,
                stack,
            )
            frame = frame.f_back
        return stack
    finally:
        frame = None


# Returns stack frame entries with the root first and the leaf last.
def unpack_stack(packed_stack):
    while packed_stack is not None:
        name, filename, firstlineno, packed_stack = packed_stack
        yield (name, filename, firstlineno)
