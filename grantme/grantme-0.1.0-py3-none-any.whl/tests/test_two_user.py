import sqlite3
import unittest

from grantme.procedures import Mode, get_status, grant, revoke
from grantme.utils.errors import *
from grantme.utils.setup import setup_db


class TwoUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        setup_db(self.conn)

        self.him = "cook"
        self.her = "julie"

    def tearDown(self):
        self.conn.close()

    def assert_emptiness(self):
        status = get_status(self.conn)
        self.assertIsNone(status)

    def assert_the_only(self, who, mode):
        status = get_status(self.conn)
        self.assertIsNotNone(status)
        self.assertEqual(status.mode, mode)
        self.assertEqual(len(status.user_expires), 1)
        self.assertIn(who, status.user_expires)

    def assert_both(self, this, that):
        status = get_status(self.conn)
        self.assertIsNotNone(status)
        self.assertEqual(status.mode, Mode.SHARED)
        self.assertEqual(len(status.user_expires), 2)
        self.assertIn(this, status.user_expires)
        self.assertIn(that, status.user_expires)

    def test_sharing(self):
        grant(self.him, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        grant(self.her, Mode.SHARED, "1m", self.conn)
        self.assert_both(self.him, self.her)

        revoke(self.him, self.conn)
        self.assert_the_only(self.her, Mode.SHARED)

        revoke(self.her, self.conn)
        self.assert_emptiness()

    def test_unique_exclusive(self):
        grant(self.him, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        with self.assertRaises(GrantmeError) as cm:
            grant(self.her, Mode.SHARED, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, GRANT_FAILURE_CODE)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        with self.assertRaises(GrantmeError) as cm:
            grant(self.her, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, GRANT_FAILURE_CODE)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        revoke(self.him, self.conn)
        self.assert_emptiness()

    def test_rmw_like_deadlock(self):
        grant(self.him, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        grant(self.her, Mode.SHARED, "1m", self.conn)
        self.assert_both(self.him, self.her)

        with self.assertRaises(GrantmeError) as cm:
            grant(self.her, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, UPGRADE_FAILURE_CODE)
        self.assert_both(self.him, self.her)

        with self.assertRaises(GrantmeError) as cm:
            grant(self.him, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, UPGRADE_FAILURE_CODE)
        self.assert_both(self.him, self.her)

        revoke(self.her, self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        revoke(self.him, self.conn)
        self.assert_emptiness()


if __name__ == "__main__":
    unittest.main()
