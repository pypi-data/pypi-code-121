import json
import sqlite3
from datetime import date, timedelta
from typing import Any, Dict, Optional

from cardtrader import get_cache_root


class SQLiteCache:
    def __init__(
        self,
        path: str = get_cache_root() / "cache.sqlite",
        expiry: Optional[int] = 14,
    ):
        self.expiry = expiry
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS queries (query, response, expiry);")
        self.delete()

    def select(self, query: str) -> Dict[str, Any]:
        if self.expiry:
            self.cur.execute(
                "SELECT response FROM queries WHERE query = ? and expiry > ?;",
                (query, date.today().isoformat()),
            )
        else:
            self.cur.execute("SELECT response FROM queries WHERE query = ?;", (query,))
        if results := self.cur.fetchone():
            return json.loads(results[0])
        return {}

    def insert(self, query: str, response: Dict[str, Any]):
        if self.expiry:
            expiry = date.today() + timedelta(days=self.expiry)
        else:
            expiry = date.today()
        self.cur.execute(
            "INSERT INTO queries (query, response, expiry) VALUES (?, ?, ?);",
            (query, json.dumps(response), expiry.isoformat()),
        )
        self.con.commit()

    def delete(self):
        if not self.expiry:
            return
        self.cur.execute("DELETE FROM queries WHERE expiry < ?;", (date.today().isoformat(),))
        self.con.commit()
