import sqlite3
import unittest


from grantme.procedures import Mode, get_status, grant, revoke
from grantme.utils.setup import setup_db


class SingleUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        setup_db(self.conn)

        self.me = "cook"

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

    def test_acquire_and_revoke_shared(self):
        grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.SHARED)

        revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_acquire_and_revoke_exclusive(self):
        grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_upgrade(self):
        grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.SHARED)

        grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_no_downgrade(self):
        grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        revoke(self.me, self.conn)
        self.assert_emptiness()


if __name__ == "__main__":
    unittest.main()
