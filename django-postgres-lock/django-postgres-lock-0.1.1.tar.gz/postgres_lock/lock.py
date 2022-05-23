from zlib import crc32

from django.db import DEFAULT_DB_ALIAS, connections


class PostgresLock:
    def __init__(self, name=None, try_=False, shared=False, using=DEFAULT_DB_ALIAS):
        # If a name isn't provided then we use the name of the database connection by default.
        # This means that the entire Django app will be using a single lock - which is probably
        # something to avoid, but is available if needed.
        if name is None:
            name = using

        self.lock_id = self.get_lock_id(name=name)
        self.try_lock = try_
        self.shared_lock = shared
        self.database_connection = connections[using]

        if try_:
            try_str = "_try"
        else:
            try_str = ""

        if shared:
            shared_str = "_shared"
        else:
            shared_str = ""

        self.lock_function = "pg{try_str}_advisory_lock{shared_str}".format(
            try_str=try_str, shared_str=shared_str
        )
        self.unlock_function = "pg_advisory_unlock{shared_str}".format(shared_str=shared_str)

    def get_lock_id(self, name):
        """
        Generate an integer suitable for Postgres advisory locks.
        """
        # Python 3 crc32 returns an unsigned integer, so we need to ensure we return a signed
        # integer instead.
        lock_id = crc32(name.encode()) & 0xFFFFFFFF
        return lock_id

    def lock(self):
        self.cursor = self.database_connection.cursor()
        self.cursor.execute(
            "SELECT {lock_function}(%(lock_id)s)".format(lock_function=self.lock_function),
            {"lock_function": self.lock_function, "lock_id": self.lock_id},
        )

        if self.try_lock:
            result = self.cursor.fetchone()[0]
        else:
            result = True

        return result

    def release(self):
        self.cursor.execute(
            "SELECT {unlock_function}(%(lock_id)s)".format(unlock_function=self.unlock_function),
            {"unlock_function": self.unlock_function, "lock_id": self.lock_id},
        )
        self.cursor.close()

    def __enter__(self):
        return self.lock()

    def __exit__(self, type, value, traceback):
        self.release()
