#!/usr/bin/env python3

"""
lang.py

Type: module

Description: a parser for a file type that makes it easier to implement
    various languages in a game

Classes:
    - LangNode
    - LangEval

Functions:
    - load(path, encoding, as_dict)
    - loads(s, encoding, as_dict, file)


Lang syntax
===========

The file can contain attributes or sets.
Attributes contain a string, while sets can contain more attributes
or other sets.

Sets
----
To declare a set use dollar sign '$' for every level of the set followed
by the name, without spaces.
The file itself is a set of level 0.
$set_of_level_1
  $$set_of_level_2

Note that a higher level set must be contained in one with a lower level.
So this:
$set_of_level_1
  $$$set_of_level_3

causes an error because a set of level 3 can be contained only in a set
of level 2.

To close a set you put a dollar sign '$' for every level of the set
that you want to close followed by an exclamation mark '!'.
If a new set with a lower or equal level is encountered, the current set
is automatically closed.

$set_of_level_1
  $$set_of_level_2_under_set_1
  $$another_set_of_level_2_under_set_1
$!

Here all the sets are closed automatically (also the explicitly
closed one if it weren't closed) and closing a set is very rare.

Attributes
----------
To declare an attribute you put an at sign '@' followed by the name of
the attribute.
@attribute1

Any line that follows, unless it's an instruction, is added to the
value of the attribute.
@attribute1
Line 1

attribute1 = 'Line 1\\n'

To give a value to the attribute on the same line use a colon ':'
@attribute1:Line 1

attribute1 = 'Line 1'

Doing this you can't set the value of the attribute to be more than
one line and there is no newline at the end of the value set.

References
----------
A reference is used to give to a new attribute the value of another.
There are two different types of references: local references and
absolute references.

Absolute references are declared with a tilde followed by an at sign '~@'
and have as base the file itself.
The attribute name and attribute value are separated by a colon ':'.
In the reference itself to access members of a set you can use dots '.',
you can access both other sets and their attributes
~@attribute_name:set.other_set.attribute

Relative references are very similar, to declare them you can use '.~@'
and have the set where they are declared as the base. This means that
you can access any attribute or child-set inside the current_set
.~@attribute_name:other_set.attribute

Comments
--------
Comments can only be at the start of a line (excluding indentation)
and are marked with '::'

$set_1
  @attr_set1
  :: This is a comment and won't be added to the value of the attribute

Encoding
--------
You can specify the type of encoding of the file preceding it with '%='.
This should be at the very first line of a file because it is reloaded
entirely if the current encoding is not correct.

Escapes
-------
If you don't want a new-line character to be added at the end of the
line you can add an and-percent '&' at the start.
To escape instructions you can use \\ at the start of the line, this
keeps any character after itself, including new-line characters,
white space, $, @, ~@, .~@, &, ::, %=, and itself (\\).
"""

import re as _re
from typing import Union as _Union

from .stack import Stack as _Stack
from .exceptions import (
    LangError as _LangError,
    LangEncodingError as _LangEncodingError
)

# With re.ASCII \w matches only [a-zA-Z0-9_]
name_expr = _re.compile(r"[a-zA-Z_]\w*", _re.ASCII)


class LangNode:
    """
    LangNode

    Type: class

    Description: a container for sets and attributes

    Methods:
        - empty()
        - get()

    All attributes and sets (sets are other LangNode objects) are set as
    attributes to the object itself

    Ex:
    lang.s.attr  # this gets the attribute 'attr' from the set 's'
    """
    def empty(self) -> None:
        """Removes all the attributes and sets the LangNode contains"""
        self.__dict__.clear()

    def get(self, s: str) -> str:
        """
        get(self, s)

        Type: method

        Description: returns an attribute or set of the node

        Args:
            's' (str): the attribute to get

        Return type: str
            In case the attribute doesn't exist inside the LangNode, it
            returns 's'

        Usage:
            in the string put the chain of attributes to access,
            separated by dots

            Ex:
            lang.get('s.attr') # this gets the attribute 'attr' from the
                               # set 's' without an error

            This can be done also by indexing the object:
            lang['s.attr']  # exactly like lang.get('s.attr')
        """
        try:
            return eval(f"self.{s}")
        except Exception:
            return s

    def __getitem__(self, idx):
        return self.get(idx)

    def __repr__(self):
        return f"LangNode({self.__dict__})"


class LangEval:
    """
    LangEval

    Type: class

    Description: a lang reference not evaluated

    Methods:
        - get_value(lang_obj)
    """
    def __init__(self, branches, local, l_no, file):
        self.branches = branches
        self.local = local
        self.l_no = l_no
        self.file = file
        self.added_value = ""

    def get_value(self, lang_obj: LangNode) -> str:
        """
        get_value(self, lang_obj)

        Type: method

        Description: evaluates the reference

        Args:
            'lang_obj' (LangNode): the node where the attribute resides
        """
        c_obj = lang_obj
        for i, v in enumerate(self.branches):
            try:
                if isinstance(c_obj, dict):
                    c_obj = c_obj[v]
                else:
                    c_obj = getattr(c_obj, v)
            except (AttributeError, KeyError):
                raise _LangError(
                    self.l_no,
                    f"the value '{'.'.join(self.branches)}' is not valid",
                    self.file
                )

            if i == len(self.branches) - 1:
                return c_obj + self.added_value

    def __add__(self, other):
        self.added_value += str(other)
        return self

    def __repr__(self):
        return f"LangEval( at '{'.'.join(self.branches)}' )"


def _make_lang_obj(d, root_node=None) -> LangNode:
    if root_node is None:
        root_node = this_node = LangNode()
    else:
        root_node = root_node
        this_node = LangNode()

    for i in d:
        v = d[i]

        if isinstance(v, dict):
            setattr(this_node, i, _make_lang_obj(v, root_node))
        elif isinstance(v, LangEval):
            if v.local:
                setattr(this_node, i, v.get_value(this_node))
            else:
                setattr(this_node, i, v.get_value(root_node))
        elif isinstance(v, str):
            setattr(this_node, i, v)

    return this_node


def _check_name(s, l_no, file) -> None:
    match = name_expr.match(s)
    if match is None or match[0] != s:
        raise _LangError(l_no, f"name '{s}' is not a valid", file)


def _make_lang_dict(s, encoding, file) -> dict:
    if isinstance(s, bytes) or isinstance(s, bytearray):
        s = s.decode(encoding)

    lines = s.split("\n")
    root = {}
    dict_stack = _Stack(root)
    attr = ""

    for l_no, l in enumerate(lines):
        if l.strip() == "": continue
        l = l.lstrip()
        if not l: continue

        if l[:2] == "%=":
            name = l[2:]
            if name.lower() != encoding.lower():
                return _LangEncodingError(f"encoding must be '{name.lower()}'")

            attr = ""
            continue

        elif l[:2] == "::": continue

        elif l[:1] == "$":
            dict_count = 0
            while l[:1] == "$":
                l = l[1:]
                dict_count += 1

            if dict_count > len(dict_stack):
                raise _LangError(
                    l_no,
                    "accessing child set with no parent",
                    file
                )

            while dict_count < len(dict_stack): dict_stack.pop()

            if l == "!": continue

            _check_name(l, l_no, file)
            dict_stack.peek()[l] = {}
            dict_stack.push(dict_stack.peek()[l])
            attr = ""
            continue

        elif l[:1] == "@":
            l = l[1:]
            colon_idx = l.find(":")
            if colon_idx != -1:
                name = l[:colon_idx]
                _check_name(name, l_no, file)
                dict_stack.peek()[name] = l[colon_idx + 1:]
                attr = ""
            else:
                _check_name(l, l_no, file)
                attr = l
            continue

        elif l[:2] == "~@" or l[:3] == ".~@":
            local = l[:3] == ".~@"

            if local: l = l[3:]
            else:     l = l[2:]

            try:
                name, val, *others = l.split(":")
            except ValueError:
                raise _LangError(l_no, "expected ':'", file)
            if others:
                raise _LangError(l_no, "invalid syntax", file)

            _check_name(name, l_no, file)
            dict_stack.peek()[name] = LangEval(val.split("."),
                                               local,
                                               l_no,
                                               file)
            attr = ""
            continue

        if l[:1] == "&": l = l[1:]
        else:
            if l[:1] == "\\": l = l[1:]
            l += "\n"

        if attr:
            try:
                dict_stack.peek()[attr] += l
            except KeyError:
                dict_stack.peek()[attr] = l
        else:
            raise _LangError(l_no, f"text with no attribute", file)

    return root


def load(path: str,
         encoding: str = "utf-8",
         as_dict: bool = False) -> _Union[LangNode, dict]:
    """
    load(path, encoding='utf-8', as_dict=False)

    Type: function

    Description: opens and parses a lang file

    Args:
        'path' (str): the path of the file
        'encoding' (str): the encoding to use when opening the file,
            defaults to utf-8
        'as_dict' (bool): if the function should return a dictionary
            instead of a LangEval object

    Return type: dict | LangNode
    """
    try:
        with open(path, encoding=encoding) as f:
            return loads(f.read(), encoding, as_dict, path)
    except _LangEncodingError as e:
        with open(path, encoding=e.args[0][17:-1]) as f:
            return loads(f.read(), e.args[0][17:-1], as_dict, path)


def loads(s: str,
          encoding: str = "utf-8",
          as_dict: bool = False,
          file: str = "<string>") -> _Union[LangNode, dict]:
    """
    loads(s, encoding='utf-8', as_dict=False, file='<string>')

    Type: function

    Description: parses a lang string

    Args:
        's' (str): the string to parse
        'encoding' (str): the encoding to use when opening the file,
            defaults to utf-8
        'as_dict' (bool): if the function should return a dictionary
            instead of a LangEval object
        'file' (str): the file of the string

    Return type: dict | LangNode
    """
    d = _make_lang_dict(s, encoding, file)
    if as_dict: return d
    return _make_lang_obj(d)
