import operator
import os
import re
from functools import reduce
from glob import glob
from operator import setitem

import click
import pygments
import pygments.formatters
import pygments.lexers

from .sql_loader import SqlLoader

terminal = pygments.formatters.get_formatter_by_name("console256")
mysql = pygments.lexers.get_lexer_by_name("mysql")

def clear_line():
    "On a tty, clears the line with carriage return, on non-tty echoes a newline"
    if click.get_text_stream('stdout').isatty():
        click.echo("\r", nl=False)
    else:
        click.echo("")

def highlight_sql(code):
    ends_with_nl = code.endswith("\n")
    c = pygments.highlight(code, mysql, terminal)
    if not ends_with_nl:
        c = c.rstrip()
    return c


def get_scripts(sqldir, mode, source, destination):
    files = glob(os.path.join(sqldir, "**/*.sql"), recursive=True)
    if len(files) == 0:
        raise click.BadParameter(
            "No script files found in {}".format(sqldir), param_hint="sqldir"
        )
    scripts = list(map(lambda fn: SqlLoader(fn), files))
    # XXX: removed the next line, pylint noticed that SqlLoader has no sort
    # method. I think get_scripts got moved to the transform step.
    # SqlLoader.sort(scripts)
    return scripts


def sort_scripts(scripts):
    return scripts.sort(key=operator.attrgetter("order"))


def filter_scripts_by_order(scripts, order):
    if re.match(r"\d+(:\d*)?(,\d+(:\d*?)?)*$", order) is None:
        raise click.ClickException(
            "Incorrect order format. I need comma separted list of order numbers or ranges in format start:end (excluding end)"
        )

    max_order = max(scripts, key=lambda s: s.order).order
    scripts_by_order = reduce(
        lambda d, s: setitem(d, s.order, d.get(s.order, []) + [s]) or d, scripts, {}
    )
    ol = order.split(",")

    def order_numbers(o):
        if ":" in o:
            start, end = o.split(":")
            if end == "":
                end = max_order + 1
            return list(range(int(start), int(end)))
        else:
            return [int(o)]

    out = []
    for o in reduce(lambda a, b: a + b, map(order_numbers, ol)):
        try:
            out += scripts_by_order.pop(o)
        except KeyError:
            pass

    return out
