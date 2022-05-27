"""
Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
76 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 Python Software
77 Foundation; All Rights Reserved
"""


def _calc___package__(globals):
    """Calculate what __package__ should be.

    __package__ is not guaranteed to be defined or could be set to None
    to represent that its proper value is unknown.

    """
    package = globals.get('__package__')
    if package is None:
        package = globals.get('__name__')

        if package is None:
            return package

        if '__path__' not in globals:
            package = package.rpartition('.')[0]
    return package


def _resolve_name(name, package, level):
    """
    Resolve a relative module name to an absolute one.
    """
    bits = package.rsplit('.', level - 1)
    if len(bits) < level:
        return None
    base = bits[0]
    return '{}.{}'.format(base, name) if name else base


def resolve_relative_import_name(name, level, globals):
    """
    Part of this code is ported from importlib._bootstrap._gcd_import in cpython

    The 'globals' argument is used to infer where the import is occurring from
    to handle relative imports.
    """
    abs_name = None

    if level <= 0 or not name or not isinstance(name, str):
        return abs_name

    package = _calc___package__(globals or {})
    if package and isinstance(package, str):
        abs_name = _resolve_name(name, package, level)

    return abs_name

