# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import pickle
import sqlite3
import time

import os

logger = logging.getLogger(__name__)


class AbstractCache(object):
    def __init__(self, cache_file: str):
        self.cache_file = cache_file

    def get(self, key: str) -> object:
        return self._get(key)

    def set(self, key: str, value: object, ttl: int = 1e10):
        return self._set(key, value, ttl)

    def unsafe_set(self, key: str, value: object, ttl: int = 1e10):
        return self._unsafe_set(key, value, ttl)

    def _set(self, key: str, value: object, ttl: int):
        raise NotImplemented

    def _unsafe_set(self, key: str, value: object, ttl: int):
        raise NotImplemented

    def _get(self, key: str) -> object:
        raise NotImplemented

    @staticmethod
    def _get_exp_time(ttl: int) -> int:
        return int(time.time() + ttl)

    @staticmethod
    def _ttl_is_timeout(exp_time: float) -> bool:
        return time.time() > exp_time


class SqliteCache(AbstractCache):
    def __init__(self, cache_file: str):
        super(SqliteCache, self).__init__(cache_file)

    def _get(self, key: str) -> object:
        conn = self._get_connect()
        try:
            value, exp_time = self._get_uid_value(conn, key)
            if exp_time is not None and not self._ttl_is_timeout(exp_time):
                return value

        except Exception as e:
            print(e)
        finally:
            conn.close()

        return None

    @staticmethod
    def _get_uid_value(conn, key):
        try:
            sql = "SELECT VALUE, EXPTIME from CACHE where UID = ?"
            cursor = conn.cursor().execute(sql, (key,))
            for row in cursor:
                return pickle.loads(row[0]), row[1]
        except Exception as e:
            logger.error(e)

        return None, None

    def _set(self, key: str, value: object, ttl: int):
        conn = self._get_connect()
        try:
            old_value, exp_time = self._get_uid_value(conn, key)
            if old_value is None and exp_time is None:
                sql = "INSERT INTO CACHE(ID, VALUE, EXPTIME, UID) VALUES (NULL, ?, ?, ?)"
            else:
                sql = "UPDATE CACHE SET VALUE = ?, EXPTIME = ? where UID = ?"

            conn.cursor().execute(sql, (pickle.dumps(value), self._get_exp_time(ttl), key))
            conn.commit()
        except Exception as e:
            logger.error(e)
            return None
        finally:
            conn.close()

    def _unsafe_set(self, key: str, value: object, ttl: int):
        logger.warning("unsafe_set == set in {}".format(self.__class__.__name__))
        return self._set(key, value, ttl)

    def _get_connect(self):
        if not os.path.exists(self.cache_file):
            conn = sqlite3.connect(self.cache_file)
            c = conn.cursor()
            c.execute('''CREATE TABLE CACHE
                   (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   UID CHAR(32) UNIQUE NOT NULL,
                   EXPTIME INT NOT NULL ,
                   VALUE TEXT);''')
            conn.commit()
            conn.close()

        return sqlite3.connect(self.cache_file)


class FileCache(AbstractCache):
    def __init__(self, pickle_file: str):
        super(FileCache, self).__init__(pickle_file)
        self.cache = self._read()

    def _read(self) -> dict:
        if not os.path.exists(self.cache_file):
            return {}

        with open(self.cache_file, "rb") as f:
            return pickle.load(f)

    def _write(self, cache):
        with open(self.cache_file, "wb") as f:
            pickle.dump(cache, f)

    def _get(self, key: str) -> object:
        val_exp = self.cache.get(key)
        if val_exp is not None:
            value, exp_time = val_exp
            if not self._ttl_is_timeout(exp_time):
                return value
            else:
                self._set(key, None, 0)

        return None

    def _set(self, key: str, value: object, ttl: int):
        self._unsafe_set(key, value, ttl)
        self._write(self.cache)

    def _unsafe_set(self, key: str, value: object, ttl: int):
        if value is None and key in self.cache:
            self.cache.pop(key)
        else:
            self.cache[key] = (value, self._get_exp_time(ttl))


__all__ = ("SqliteCache", "FileCache", "AbstractCache")
