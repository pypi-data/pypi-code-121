#  Copyright (c) 2016, 2018-2021 by Rocky Bernstein
#  Copyright (c) 2005 by Dan Pascu <dan@windowmaker.org>
#  Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
#  Copyright (c) 1999 John Aycock
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
scanner/ingestion module. From here we call various version-specific
scanners, e.g. for Python 3.7 or 3.8.
"""

import xdis
from typing import Optional
from array import array
from collections import namedtuple
from xdis.version_info import IS_PYPY, version_tuple_to_str
from xdis import (
    Bytecode,
    canonic_python_version,
    code2num,
    extended_arg_val,
    instruction_size,
    next_offset,
)

from decompyle3.scanners.tok import Token

# The byte code versions we support.
# Note: these all have to be floats
PYTHON_VERSIONS = frozenset(((3, 7), (3, 8), (3, 9)))

CANONIC2VERSION = dict(
    (canonic_python_version[version_tuple_to_str(python_version)], python_version)
    for python_version in PYTHON_VERSIONS
)

L65536 = 65536


def long(num):
    return num


class Code(object):
    """
    Class for representing code-objects.

    This is similar to the original code object, but additionally
    the diassembled code is stored in the attribute '_tokens'.
    """

    def __init__(self, co, scanner, classname=None, show_asm=None):
        for i in dir(co):
            if i.startswith("co_"):
                setattr(self, i, getattr(co, i))
        self._tokens, self._customize = scanner.ingest(co, classname, show_asm=show_asm)


class Scanner(object):
    def __init__(self, version: tuple, show_asm=None, is_pypy=False):
        self.version = version
        self.show_asm = show_asm
        self.is_pypy = is_pypy

        if version[:2] in PYTHON_VERSIONS:
            v_str = f"""opcode_{version_tuple_to_str(version, start=0, end=2, delimiter="")}"""
            if is_pypy:
                v_str += "pypy"
            exec(f"""from xdis.opcodes import {v_str}""")
            exec("self.opc = %s" % v_str)
        else:
            raise TypeError(
                "%s is not a Python version I know about"
                % version_tuple_to_str(version)
            )

        self.opname = self.opc.opname

        # FIXME: This weird Python2 behavior is not Python3
        self.resetTokenClass()

    def build_instructions(self, co):
        """
        Create a list of instructions (a structured object rather than
        an array of bytes) and store that in self.insts
        """
        # FIXME: remove this when all subsidiary functions have been removed.
        # We should be able to get everything from the self.insts list.
        self.code = array("B", co.co_code)

        bytecode = Bytecode(co, self.opc)
        self.build_prev_op()
        self.insts = self.remove_extended_args(list(bytecode))
        self.lines = self.build_lines_data(co)
        self.offset2inst_index = {}
        for i, inst in enumerate(self.insts):
            self.offset2inst_index[inst.offset] = i

        return bytecode

    def build_lines_data(self, code_obj):
        """
        Generate various line-related helper data.
        """

        # Offset: lineno pairs, only for offsets which start line.
        # Locally we use list for more convenient iteration using indices
        if self.version > (1, 4):
            linestarts = list(self.opc.findlinestarts(code_obj))
        else:
            linestarts = [[0, 1]]
        self.linestarts = dict(linestarts)

        # 'List-map' which shows line number of current op and offset of
        # first op on following line, given offset of op as index
        lines = []
        LineTuple = namedtuple("LineTuple", ["l_no", "next"])

        # Iterate through available linestarts, and fill
        # the data for all code offsets encountered until
        # last linestart offset
        _, prev_line_no = linestarts[0]
        offset = 0
        for start_offset, line_no in linestarts[1:]:
            while offset < start_offset:
                lines.append(LineTuple(prev_line_no, start_offset))
                offset += 1
            prev_line_no = line_no

        # Fill remaining offsets with reference to last line number
        # and code length as start offset of following non-existing line
        codelen = len(self.code)
        while offset < codelen:
            lines.append(LineTuple(prev_line_no, codelen))
            offset += 1
        return lines

    def build_prev_op(self):
        """
        Compose 'list-map' which allows to jump to previous
        op, given offset of current op as index.
        """
        code = self.code
        codelen = len(code)
        # 2.x uses prev 3.x uses prev_op. Sigh
        # Until we get this sorted out.
        self.prev = self.prev_op = [0]
        for offset in self.op_range(0, codelen):
            op = code[offset]
            for _ in range(instruction_size(op, self.opc)):
                self.prev_op.append(offset)

    def is_jump_forward(self, offset: int) -> bool:
        """
        Return True if the code at offset is some sort of jump forward.
        That is, it is ether "JUMP_FORWARD" or an absolute jump that
        goes forward.
        """
        opname = self.get_inst(offset).opname
        if opname == "JUMP_FORWARD":
            return True
        if opname != "JUMP_ABSOLUTE":
            return False
        return offset < self.get_target(offset)

    def prev_offset(self, offset: int) -> int:
        return self.insts[self.offset2inst_index[offset] - 1].offset

    def get_inst(self, offset: int):
        # Instructions can get moved as a result of EXTENDED_ARGS removal.
        # So if "offset" is not in self.offset2inst_index, then
        # we assume that it was an instruction moved back.
        # We check that assumption though by looking at
        # self.code's opcode.
        # Sadly instructions can get moved _forward too.
        # So we have to check which direction we are going
        offset_increment = instruction_size(self.opc.EXTENDED_ARG, self.opc)
        if offset not in self.offset2inst_index:
            if self.code[offset] != self.opc.EXTENDED_ARG:
                target_name = self.opc.opname[self.code[offset]]
                # JUMP_ABSOLUTE can be like this where
                # the inst offset is at what used to be an EXTENDED_ARG
                # so find the first extended arg.
                next_offset = offset - offset_increment
                while next_offset not in self.offset2inst_index:
                    next_offset -= offset_increment
                    assert self.code[next_offset] == self.opc.EXTENDED_ARG
                inst = self.insts[self.offset2inst_index[next_offset]]
                assert inst.opname == target_name, inst
            else:
                next_offset = offset + offset_increment
                while next_offset not in self.offset2inst_index:
                    next_offset += offset_increment

                inst = self.insts[self.offset2inst_index[next_offset]]

            assert inst.has_extended_arg is True
            return inst

        return self.insts[self.offset2inst_index[offset]]

    def get_target(self, offset: int, extended_arg: int = 0) -> int:
        """
        Get next instruction offset for op located at given <offset>.
        NOTE: extended_arg is no longer used
        """
        inst = self.get_inst(offset)
        if inst.opcode in self.opc.JREL_OPS | self.opc.JABS_OPS:
            target = inst.argval
        else:
            # No jump offset, so use fall-through offset
            target = next_offset(inst.opcode, self.opc, inst.offset)
        return target

    def get_argument(self, pos: int):
        arg = self.code[pos + 1] + self.code[pos + 2] * 256
        return arg

    def next_offset(self, op, offset: int) -> int:
        return xdis.next_offset(op, self.opc, offset)

    def print_bytecode(self):
        for i in self.op_range(0, len(self.code)):
            op = self.code[i]
            if op in self.JUMP_OPS:
                dest = self.get_target(i, op)
                print("%i\t%s\t%i" % (i, self.opname[op], dest))
            else:
                print("%i\t%s\t" % (i, self.opname[op]))

    def first_instr(self, start: int, end: int, instr, target=None, exact=True):
        """
        Find the first <instr> in the block from start to end.
        <instr> is any python bytecode instruction or a list of opcodes
        If <instr> is an opcode with a target (like a jump), a target
        destination can be specified which must match precisely if exact
        is True, or if exact is False, the instruction which has a target
        closest to <target> will be returned.

        Return index to it or None if not found.
        """
        code = self.code
        assert start >= 0 and end <= len(code)

        if not isinstance(instr, list):
            instr = [instr]

        result_offset = None
        current_distance = len(code)
        for offset in self.op_range(start, end):
            op = code[offset]
            if op in instr:
                if target is None:
                    return offset
                dest = self.get_target(offset)
                if dest == target:
                    return offset
                elif not exact:
                    new_distance = abs(target - dest)
                    if new_distance < current_distance:
                        current_distance = new_distance
                        result_offset = offset
        return result_offset

    def last_instr(
        self, start: int, end: int, instr, target=None, exact=True
    ) -> Optional[int]:
        """
        Find the last <instr> in the block from start to end.
        <instr> is any python bytecode instruction or a list of opcodes
        If <instr> is an opcode with a target (like a jump), a target
        destination can be specified which must match precisely if exact
        is True, or if exact is False, the instruction which has a target
        closest to <target> will be returned.

        Return index to it or None if not found.
        """

        code = self.code
        # Make sure requested positions do not go out of
        # code bounds
        if not (start >= 0 and end <= len(code)):
            return None

        if not isinstance(instr, list):
            instr = [instr]

        result_offset = None
        current_distance = self.insts[-1].offset - self.insts[0].offset
        extended_arg = 0
        # FIXME: use self.insts rather than code[]
        for offset in self.op_range(start, end):
            op = code[offset]

            if op == self.opc.EXTENDED_ARG:
                arg = code2num(code, offset + 1) | extended_arg
                extended_arg = extended_arg_val(self.opc, arg)
                continue

            if op in instr:
                if target is None:
                    result_offset = offset
                else:
                    dest = self.get_target(offset, extended_arg)
                    if dest == target:
                        current_distance = 0
                        result_offset = offset
                    elif not exact:
                        new_distance = abs(target - dest)
                        if new_distance <= current_distance:
                            current_distance = new_distance
                            result_offset = offset
                            pass
                        pass
                    pass
                pass
            extended_arg = 0
            pass
        return result_offset

    def inst_matches(self, start, end, instr, target=None, include_beyond_target=False):
        """
        Find all `instr` in the block from start to end.
        `instr` is a Python opcode or a list of opcodes
        If `instr` is an opcode with a target (like a jump), a target
        destination can be specified which must match precisely.

        Return a list with indexes to them or [] if none found.
        """
        try:
            None in instr
        except Exception:
            instr = [instr]

        first = self.offset2inst_index[start]
        result = []
        for inst in self.insts[first:]:
            if inst.opcode in instr:
                if target is None:
                    result.append(inst.offset)
                else:
                    t = self.get_target(inst.offset)
                    if include_beyond_target and t >= target:
                        result.append(inst.offset)
                    elif t == target:
                        result.append(inst.offset)
                        pass
                    pass
                pass
            if inst.offset >= end:
                break
            pass

        # FIXME: put in a test
        # check = self.all_instr(start, end, instr, target, include_beyond_target)
        # assert result == check

        return result

    # FIXME: this is broken on 3.6+. Replace remaining (2.x-based) calls
    # with inst_matches

    def all_instr(
        self, start: int, end: int, instr, target=None, include_beyond_target=False
    ):
        """
        Find all `instr` in the block from start to end.
        `instr` is any Python opcode or a list of opcodes
        If `instr` is an opcode with a target (like a jump), a target
        destination can be specified which must match precisely.

        Return a list with indexes to them or [] if none found.
        """

        code = self.code
        assert start >= 0 and end <= len(code)

        if not isinstance(instr, list):
            instr = [instr]

        result = []
        extended_arg = 0
        for offset in self.op_range(start, end):

            op = code[offset]

            if op == self.opc.EXTENDED_ARG:
                arg = code2num(code, offset + 1) | extended_arg
                extended_arg = extended_arg_val(self.opc, arg)
                continue

            if op in instr:
                if target is None:
                    result.append(offset)
                else:
                    t = self.get_target(offset, extended_arg)
                    if include_beyond_target and t >= target:
                        result.append(offset)
                    elif t == target:
                        result.append(offset)
                        pass
                    pass
                pass
            extended_arg = 0
            pass

        return result

    def opname_for_offset(self, offset):
        return self.opc.opname[self.code[offset]]

    def op_name(self, op):
        return self.opc.opname[op]

    def op_range(self, start, end):
        """
        Iterate through positions of opcodes, skipping
        arguments.
        """
        while start < end:
            yield start
            start += instruction_size(self.code[start], self.opc)

    def remove_extended_args(self, instructions):
        """Go through instructions removing extended ARG.
        get_instruction_bytes previously adjusted the operand values
        to account for these"""
        new_instructions = []
        last_was_extarg = False
        n = len(instructions)
        for i, inst in enumerate(instructions):
            if (
                inst.opname == "EXTENDED_ARG"
                and i + 1 < n
                and instructions[i + 1].opname != "MAKE_FUNCTION"
            ):
                last_was_extarg = True
                starts_line = inst.starts_line
                is_jump_target = inst.is_jump_target
                offset = inst.offset
                continue
            if last_was_extarg:

                # j = self.stmts.index(inst.offset)
                # self.lines[j] = offset

                new_inst = inst._replace(
                    starts_line=starts_line,
                    is_jump_target=is_jump_target,
                    offset=offset,
                )
                inst = new_inst
                if i < n:
                    new_prev = self.prev_op[instructions[i].offset]
                    j = instructions[i + 1].offset
                    old_prev = self.prev_op[j]
                    while self.prev_op[j] == old_prev and j < n:
                        self.prev_op[j] = new_prev
                        j += 1

            last_was_extarg = False
            new_instructions.append(inst)
        return new_instructions

    def remove_mid_line_ifs(self, ifs):
        """
        Go through passed offsets, filtering ifs
        located somewhere mid-line.
        """

        # FIXME: this doesn't work for Python 3.6+

        filtered = []
        for i in ifs:
            # For each offset, if line number of current and next op
            # is the same
            if self.lines[i].l_no == self.lines[i + 3].l_no:
                # Skip last op on line if it is some sort of POP_JUMP.
                if self.code[self.prev[self.lines[i].next]] in (
                    self.opc.PJIT,
                    self.opc.PJIF,
                ):
                    continue
            filtered.append(i)
        return filtered

    def resetTokenClass(self):
        return self.setTokenClass(Token)

    def restrict_to_parent(self, target: int, parent) -> int:
        """Restrict target to parent structure boundaries."""
        if not (parent["start"] < target < parent["end"]):
            target = parent["end"]
        return target

    def setTokenClass(self, tokenClass) -> Token:
        self.Token = tokenClass
        return self.Token


def parse_fn_counts(argc):
    return ((argc & 0xFF), (argc >> 8) & 0xFF, (argc >> 16) & 0x7FFF)


def get_scanner(version, is_pypy=False, show_asm=None):

    # If version is a string, turn that into the corresponding float.
    if isinstance(version, str):
        if version not in canonic_python_version:
            raise RuntimeError(f"Unknown Python version in xdis {version}")
        canonic_version = canonic_python_version[version]
        if canonic_version not in CANONIC2VERSION:
            raise RuntimeError(
                f"Unsupported Python version {version} (canonic {canonic_version})"
            )
        version = CANONIC2VERSION[canonic_version]

    # Pick up appropriate scanner
    if version[:2] in PYTHON_VERSIONS:
        v_str = version_tuple_to_str(version, start=0, end=2, delimiter="")
        try:
            import importlib

            if is_pypy:
                scan = importlib.import_module("decompyle3.scanners.pypy%s" % v_str)
            else:
                scan = importlib.import_module("decompyle3.scanners.scanner%s" % v_str)
            if False:
                print(scan)  # Avoid unused scan
        except ImportError:
            if is_pypy:
                exec(
                    "import decompyle3.scanners.pypy%s as scan" % v_str,
                    locals(),
                    globals(),
                )
            else:
                exec(
                    "import decompyle3.scanners.scanner%s as scan" % v_str,
                    locals(),
                    globals(),
                )
        if is_pypy:
            scanner = eval(
                "scan.ScannerPyPy%s(show_asm=show_asm)" % v_str, locals(), globals()
            )
        else:
            scanner = eval(
                "scan.Scanner%s(show_asm=show_asm)" % v_str, locals(), globals()
            )
    else:
        raise RuntimeError(
            f"Unsupported Python version, {version_tuple_to_str(version)}, for decompilation"
        )
    return scanner


if __name__ == "__main__":
    import inspect

    co = inspect.currentframe().f_code
    from xdis.version_info import PYTHON_VERSION_TRIPLE

    scanner = get_scanner(PYTHON_VERSION_TRIPLE, IS_PYPY, True)
    tokens, customize = scanner.ingest(co, {}, show_asm="after")
