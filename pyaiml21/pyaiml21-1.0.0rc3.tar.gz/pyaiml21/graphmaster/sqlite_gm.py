"""Graphmaster based on sqlite3."""
import sqlite3
from typing import Union, Any

import dill

from pyaiml21.botconfig import BotConfig
from .graphmaster import GraphMaster, PolicyFn, KEEP_LAST_POLICY


class SqLiteGraphMaster(GraphMaster):
    """
    Store the template nodes in the sqlite database.

    For more details on the graphmaster, please refer to the
    ``GraphMaster`` implementation.

    The constructor expects a `sqlite3.Connection` object, it is the
    responsibility of the user to make sure the connection stays open
    during the lifetime of the graphmaster.
    """

    _TABLE_NAME = "graphmaster_templates"
    _COLUMN_NAME = "pickled_template"
    _CREATE_TABLE = f"CREATE TABLE IF NOT EXISTS {_TABLE_NAME} " \
                    f"({_COLUMN_NAME} text)"

    def __init__(
            self,
            bot_config: 'BotConfig',
            conn: sqlite3.Connection,
            policy: Union[str, PolicyFn] = KEEP_LAST_POLICY
    ):
        """
        Create sqlite3 graphmaster.

        :param conn: sqlite connection to store the graphmaster data into,
            the name of the table to which the pickled objects will be stored
            can be accessed via `SqLiteGraphMaster._TABLE_NAME`
        :param bot_config: configuration of the bot with sets and predicates
        :param policy: merge policy to use
        """
        super().__init__(bot_config, policy)
        self.cursor = conn.cursor()
        self.cursor.execute(self._CREATE_TABLE)

    def save_obj(self, obj: Any) -> int:
        """Save `obj` to the database."""
        pickled_obj = dill.dumps(obj)
        self.cursor.execute(
            f"INSERT INTO {self._TABLE_NAME} "
            f"VALUES (?)", (pickled_obj,)
        )
        row_id = self.cursor.lastrowid
        self.cursor.connection.commit()
        assert row_id is not None
        assert isinstance(row_id, int)
        return row_id

    def load_obj(self, saved_obj: int) -> Any:
        """Load template from the database."""
        self.cursor.execute(
            f"SELECT {self._COLUMN_NAME} FROM {self._TABLE_NAME} "
            f"WHERE rowid = (?)", (saved_obj,)
        )
        from_db = self.cursor.fetchone()[0]  # 1-tuple :D
        return dill.loads(from_db)
