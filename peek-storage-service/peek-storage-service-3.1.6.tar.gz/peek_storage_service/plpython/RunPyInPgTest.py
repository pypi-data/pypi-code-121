import logging
import unittest
from typing import List

from peek_storage_service._private.test.StorageTestMixin import StorageTestMixin
from peek_storage_service.plpython.RunPyInPg import runPyInPgBlocking

logger = logging.getLogger(__name__)


class RunPyInPgTestCase(unittest.TestCase, StorageTestMixin):
    def __init__(self, methodName="runTest"):
        unittest.TestCase.__init__(self, methodName)

        self._dbConn = None

    def setUp(self) -> None:
        StorageTestMixin.setUp(self)

    def tearDown(self) -> None:
        StorageTestMixin.tearDown(self)

    # -------------------------------------------------------------------------
    def test_args(self):
        result = runPyInPgBlocking(
            self._dbConn.ormSessionCreator, self._pg_args, None, ["SUC", "CESS"]
        )

        self.assertEqual(result, "SUCCESS")

    @classmethod
    def _pg_args(cls, plpy, successes: List[str]):
        return "".join(successes)

    # -------------------------------------------------------------------------
    def test_kwwargs(self):
        result = runPyInPgBlocking(
            self._dbConn.ormSessionCreator,
            self._pg_kwargs,
            None,
            suc="SUC",
            cess="CESS KW",
        )

        self.assertEqual(result, "SUCCESS KW")

    @classmethod
    def _pg_kwargs(cls, plpy, suc, cess):
        return suc + cess

    # -------------------------------------------------------------------------
    def test_pypg(self):
        result = runPyInPgBlocking(self._dbConn.ormSessionCreator, self._pg_plpy)

        self.assertEqual(result, "plpy exists")

    @classmethod
    def _pg_plpy(cls, plpy):
        assert plpy, "pypg is not defined"

        return "plpy exists"

    # -------------------------------------------------------------------------
