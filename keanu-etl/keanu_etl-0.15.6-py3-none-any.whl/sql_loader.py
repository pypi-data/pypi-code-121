import os
import re
import shutil
from glob import glob

import click
from pymysql.err import MySQLError
from sqlalchemy.exc import DataError, InternalError, ProgrammingError

from . import tracing
from .batch import RetryScript
from .run_statement import RunStatement


class SqlLoader(RunStatement, tracing.Tags):
    """
    Class that runs load scripts, that is SQL that loads some data in keanu database.
    It can read extra metadata from the script comments.

    Pass path to file of SQL script.

    options can be:
    incremental - run incremental variant of the script (no by default)
    display - displays full SQL while executing (no by default)
    warn - do show warnings from mysql driver (no by default)
    """

    def __init__(self, filename, mode=None, source=None, destination=None):
        super().__init__()

        # filename and class options
        self.filename = filename
        self.options = {"incremental": False, "display": False, "warn": False}
        self.options.update(mode)
        self.source = source
        self.destination = destination

        # defaults
        self.deleteSql = []
        self.order = 100

        # parse SQL
        self.lines = self.parse(open(filename, "r").readlines())
        self.statements = self.split_statements(self.lines)

    @staticmethod
    def from_directory(sqldir, mode, source, destination):
        files = glob(os.path.join(sqldir, "**/*.sql"), recursive=True)
        if len(files) == 0:
            raise click.BadParameter(
                "No script files found in {}".format(sqldir), param_hint="config_or_dir"
            )
        scripts = list(map(lambda fn: SqlLoader(fn, mode, source, destination), files))
        return scripts

    def __str__(self):
        return "{} ({})".format(self.filename, self.order)

    """
    Parse script lines and load metadata. Returns list of lines after parsing (will be modified).
    Has effects of setting fields on object.
    """

    def parse(self, lines):
        out = []
        contexts = []
        comment_line = lambda x: "-- " + x

        lines = map(self.interpolate_environ, lines)

        flv = self.flavor(self.destination.connection())

        for l in lines:
            m = re.match(r" *-- *ORDER: (\d+)", l)
            if m:
                self.order = int(m.group(1))
                continue

            m = re.match(r" *-- *TAGS: ?(.+)$", l)
            if m:
                kv = {
                    x.group(1): x.group(2)
                    for x in re.finditer(r"([\w\d_-]+) *= *([\w\d_-]+)", m.group(1))
                }
                self.tracing_tags.update(kv)

                continue

            m = re.match(r" *-- *((DELETE|TRUNCATE) .*)$", l)
            if m:
                self.deleteSql.append(m.group(1))
                continue

            m = re.match(r" *-- *BEGIN (\w+)", l)
            if m:
                contexts.append(m.group(1).upper())
                continue

            m = re.match(r" *-- *END (\w+)", l)
            if m:
                try:
                    contexts.remove(m.group(1).upper())
                except ValueError:
                    raise ValueError(
                        "{}: found END {} but context stack is {}".format(
                            self.filename, m.group(1), ", ".join(contexts)
                        )
                    )
                continue

            m = re.match(r" *-- *IGNORE", l)
            if m:
                break

            if "INCREMENTAL" in contexts and not self.options["incremental"]:
                l = comment_line(l)

            if "INITIAL" in contexts and self.options["incremental"]:
                l = comment_line(l)

            if any(map(lambda x: x in contexts, ["MYSQL", "POSTGRESQL"])) and flv.upper() not in contexts:
                l = comment_line(l)

            out.insert(0, l)

        if len(contexts) > 0:
            raise ValueError(
                "Script {} ended with contexts {} unclosed",
                self.filename,
                ", ".join(contexts),
            )

        out.reverse()
        return out

    """
    Performs interpolation on string, replacing ${FOO} with FOO environment variable.
    """

    def interpolate_environ(self, line):
        env = {}
        if self.source:
            env.update(self.source.environ())
        if self.destination:
            env.update(self.destination.environ())

        def get_var(m):
            k = m.group(1)
            if k in env:
                if isinstance(env[k], list):
                    return str(env[k])[1:-1]  # return 'elem','elem2' without surrounding [ ] 
                else:
                    return str(env[k])
            return os.environ[k]

        return re.subn(r"[$]{([A-Za-z1-9_]+)}", get_var, line)[0]

    """
    Predicate - is this line just a comment line?
    """

    @staticmethod
    def noop_line(line):
        return (re.match(r" *--", line) or re.match(r"^[\s;]*$", line)) is not None

    """
    Will split the lines of script into SQL statements (separated by semicolon)
    """

    def split_statements(self, lines):
        def non_empty_block(statements):
            return len(statements) > 0 and any(
                map(lambda a: not self.noop_line(a), statements)
            )

        # output list of statement lists, and current list
        out = []
        c = []

        # current delimiter
        delimiter = ";"

        for l in lines:
            # For delimiter MySQL client command, change the regex and continue
            m = re.match(r"DELIMITER (.+)\s*$", l)
            if m:
                delimiter = re.escape(m.group(1))
                continue

            # For end of statement block (according to delimiter), store in out
            m = re.search(r"(.*)" + delimiter + r"\s*($|--.*$)", l)
            if m:
                c.append(m.group(1))

                if non_empty_block(c):
                    out.append(c)
                c = []
            else:
                c.append(l)

        # join lines into str for each statement
        return list(map(lambda a: "".join(a).lstrip(), out))

    def replace_sql_object(self, before, after):
        before = "`{}`".format(before)
        after = "`{}`".format(after)
        self.statements = list(
            map(lambda st: st.replace(before, after), self.statements)
        )

    def statement_abbrev(self, statement):
        if self.options["display"]:
            return statement

        trim_to = int(shutil.get_terminal_size((200, 20)).columns * 0.7)

        lines = statement.split("\n")
        lines = filter(
            lambda x: not re.match(r" *--", x) and not re.match(r"\s*$", x), lines
        )
        try:
            first = next(lines)
            if len(first) > trim_to:
                first = first[0:trim_to] + "..."
            return first
        except StopIteration:
            return ""

    def delete(self):
        if len(self.deleteSql) == 0:
            return

        connection = self.destination.connection()
        with tracing.span(
            "delete.{}".format(self.filename.replace("/", ".")), tags=self.tracing_tags
        ):
            with connection.begin() as transaction:
                yield "sql.script.start.delete", {"script": self}
                try:
                    for event, data in super().execute(
                        connection, self.deleteSql, warn=self.options["warn"]
                    ):
                        yield event, data
                except KeyboardInterrupt as ctrlc:
                    transaction.rollback()
                    raise ctrlc
                yield "sql.script.end.delete", {"script": self}

    def display_error(self, e):
        msg = str(e.args[0])
        msg = msg.replace("\\n", "\n")
        click.echo(message=msg, err=True)
        return msg

    def execute(self):
        if len(self.statements) == 0:
            return

        connection = self.destination.connection()
        with tracing.span(
            "script.{}".format(self.filename.replace("/", ".")), tags=self.tracing_tags
        ):
            with connection.begin() as transaction:
                try:
                    yield "sql.script.start", {"script": self}
                    for event, data in super().execute(
                        connection, self.statements, warn=self.options["warn"]
                    ):
                        yield event, data
                    yield "sql.script.end", {"script": self}
                except KeyboardInterrupt:
                    transaction.rollback()
                    raise click.Abort("aborted.")
                except (ProgrammingError, MySQLError, DataError) as e:
                    transaction.rollback()
                    raise click.Abort(self.display_error(e))
                except InternalError as e:
                    if "Lock wait timeout exceeded" in e.orig.args[1]:
                        raise RetryScript() from e
                    else:
                        transaction.rollback()
                        raise click.Abort(self.display_error(e))
