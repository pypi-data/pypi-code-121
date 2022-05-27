# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Implements a single API for instrumenting all dbapi2-compliant modules
"""
import contrast
from contrast.applies.sqli import apply_rule
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch


class Dbapi2Patcher(object):
    """
    Do not instantiate this class; call `instrument_adapter` or subclass it.

    This class provides machinery to instrument a totally generic, PEP-249 compliant
    adapter. We only have a reference to the adapter module, and we can't make any
    assumptions about the existence of `adapter.Cursor`, since this is not guaranteed
    by the spec.

    We are only guaranteed the following:
    - the adapter has a `connection()` method, which returns an instance of Connection
    - the Connection object has a `cursor()` method, which returns an instance of Cursor
    - the Cursor has `execute()` and `executemany()` methods

    This requires a somewhat roundabout instrumentation strategy:
    - on the first call to adapter.connect(), we can instrument the Connection class
    - on the first call to Connection.cursor(), we can instrument the Cursor class
    - this lets us instrument Cursor.execute() and Cursor.executemany()
    """

    def __init__(self, adapter, vendor):
        self.dbinfo = {"vendor": vendor}
        self.vendor = vendor

        self._adapter = adapter
        # this module name must match a policy node; we need to fake sqlalchemy
        self._adapter_name = (
            "sqlalchemy" if self.vendor == "sqlalchemy" else self._adapter.__name__
        )
        self._connect_called = False
        self._cursor_called = False

    @fail_quietly("failed to instrument database adapter")
    def instrument(self, extra_cursors):
        build_and_apply_patch(self._adapter, "connect", self._build_connect_patch)
        for cursor in extra_cursors:
            self._safe_instrument_cursor(cursor)

    @fail_quietly("failed to get database inventory information")
    def init_dbinfo(self, connection, connect_args, connect_kwargs):
        """
        This method is intended to be overridden by subclasses if necessary. It must add
        key-value pairs to `dbinfo` - any/all of host", "port", and "database" (ie
        dbname). "vendor" should already be populated.

        Takes the arguments from a call to connect() and extracts information for
        database inventory reporting. By default only works with kwargs - we expect this
        to be by far the most common case.

        This follows the conventions laid out in the footnotes of dbapi2:
        https://www.python.org/dev/peps/pep-0249/#footnote-1

        In SQLAlchemy, see create_connect_args() for each dialect to get an idea of how
        different adapters are used. Most, if not all, use kwargs. Some adapters support
        a DSN connection string, but that should be handled by subclasses (if at all).
        """
        for key in ["host", "port"]:
            if key in connect_kwargs:
                self.dbinfo[key] = connect_kwargs[key]

        # the database name argument has several variations
        for key in ["database", "dbname", "db"]:
            if key in connect_kwargs:
                self.dbinfo["database"] = connect_kwargs[key]
                break

    @fail_quietly("failed to instrument database cursor class")
    def _safe_instrument_cursor(self, cursor_class):
        """
        Instruments a dbapi2-compliant database cursor class

        @param cursor_class: Reference to cursor class to be instrumented
        """
        self._instrument_cursor_method(cursor_class, "execute")
        self._instrument_cursor_method(cursor_class, "executemany")
        if hasattr(cursor_class, "executescript"):
            # non-standard, but provided by some adapters such as sqlite3
            self._instrument_cursor_method(cursor_class, "executescript")

    def _instrument_cursor_method(self, cursor, method_name):
        build_and_apply_patch(
            cursor,
            method_name,
            self._build_execute_patch,
        )

    @fail_quietly("failed to instrument database connection object")
    def _safe_instrument_connection(self, connection_instance):
        """
        Instruments a dbapi2-compliant database connection class, given an instance

        @param connection_instance: dbapi2 Connection instance
        """
        connection_class = type(connection_instance)
        build_and_apply_patch(connection_class, "cursor", self._build_cursor_patch)

    @property
    def _build_execute_patch(self):
        """
        See `_build_connect_patch`
        """

        def build_execute_patch(orig_func, patch_policy):
            def patched_method(*args, **kwargs):
                """
                Patch for dbapi_adapter.connection().cursor().execute*()
                """
                self._safe_append_dbinfo_to_context()
                return apply_rule(self._adapter_name, orig_func, args, kwargs)

            return patched_method

        return build_execute_patch

    @property
    def _build_cursor_patch(self):
        """
        See `_build_connect_patch`
        """

        def build_cursor_patch(orig_func, _):
            def cursor_patch(*args, **kwargs):
                """
                Patch for dbapi_adapter.connection().cursor()

                This patch will ensure that the returned Cursor object's class will have
                `execute` and `executemany` instrumented.
                """
                cursor = orig_func(*args, **kwargs)
                if not self._cursor_called:
                    try:
                        cursor_class = type(cursor)
                        self._safe_instrument_cursor(cursor_class)
                        self._cursor_called = True
                    except Exception:
                        pass
                return cursor

            return cursor_patch

        return build_cursor_patch

    @property
    def _build_connect_patch(self):
        """
        Getter for `build_connect_patch`. We can't just make `build_connect_patch` an
        instance method because of the added `self` argument.
        """

        def build_connect_patch(orig_func, _):
            def connect_patch(*args, **kwargs):
                """
                Patch for dbapi_adapter.connection()

                This patch will ensure that the returned Connection object's class will
                have `cursor_patch` applied to its cursor() method.
                """
                connection = orig_func(*args, **kwargs)
                if not self._connect_called:
                    self.init_dbinfo(connection, args, kwargs)
                    self._safe_instrument_connection(connection)
                    self._connect_called = True
                self._safe_append_dbinfo_to_context()
                return connection

            return connect_patch

        return build_connect_patch

    @fail_quietly("failed to add database information to context")
    def _safe_append_dbinfo_to_context(self):
        """
        Add the given database information to context.activity
        """
        context = contrast.CS__CONTEXT_TRACKER.current()
        if not context:
            return
        context.database_info.append(self.dbinfo)


@fail_quietly("failed to instrument database adapter")
def instrument_adapter(adapter, vendor, patcher_cls=Dbapi2Patcher, extra_cursors=None):
    """
    Instrument the provided dbapi2 adapter.

    `vendor` must be a string that exactly matches a value from Teamserver's
    flowmap/technologies.json > service > one of "name".

    References to cursors to instrument explicitly can be passed in via extra_cursors.
    If we could guarantee patches were applied before any calls to `adapter.connect()`,
    we wouldn't need to directly patch extra cursors - unfortunately, this probably
    means we'd need to be a runner.
    """
    patcher_cls(adapter, vendor).instrument(extra_cursors or [])
