from sqlalchemy.orm import sessionmaker

from .data_store import DataStore
from . import db


class DBDestination(DataStore):
    def __init__(self, spec, name=None, dry_run=False):
        super().__init__(name, spec, dry_run)
        if not self.local:
            self.engine = db.get_engine(self.url, self.dry_run)
            self.Session = sessionmaker(bind=self.engine)

    def connection(self):
        if not self.local:
            conn = self.threadsafe_connection
        else:
            src = self.batch.find_source(lambda s: s.local == False)
            conn = src.connection()
        return conn

    def session(self):
        if not self.local:
            return self.Session()
        # Not implemented
        return None

    def environ(self):
        env = {}

        if 'env' in self.config:
            env = {**self.config['env'], **env}

        return env
