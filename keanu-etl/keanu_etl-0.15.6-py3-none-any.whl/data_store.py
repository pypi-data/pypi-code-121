from pytz import utc, timezone
from . import db
import threading

class DataStore:
    """
    Arguments:

    name - name for the store
    db_spec - connection specification

    Parameters:

    dry_run - do not really execute reads or writes on store

    Properties set by constructor

    - name - name of this data store, can be used to refer it in config find in in batch
    - config - returns the whole data store definition
    - batch - can link to batch using this data store
    - url - url to the data store.
    - local - is it part of other data store
    - schema - or logical "database", but in general case path in store url. Would also work for an AMQP vhost for example
    """

    def __init__(self, name, spec, dry_run=False):
        db_spec = spec["db"]

        self.name = name
        self.local = False
        self._spec = spec
        self.dry_run = dry_run
        self.batch = None

        # schema and connection are used in DataStore,
        # they should be moved there
        self.url = db_spec.get("url", None)
        self.schema = db_spec.get("schema", None) or db.url_to_schema(self.url)
        self.local = self.url is None

        if not self.local:
            self.engine = db.get_engine(self.url, self.dry_run)

        if 'timezone' in spec:
            self.timezone = timezone(spec['timezone'])
        else:
            self.timezone = utc

        self.thread_local = threading.local()

    def set_batch(self, b):
        self.batch = b

    @property
    def config(self):
        return self._spec

    @property
    def threadsafe_connection(self):
        tl = self.thread_local
        if not hasattr(tl, "connection"):
            tl.connection = self.engine.connect()
        return tl.connection

    def threadsafe_close(self):
        tl = self.thread_local
        if hasattr(tl, "connection"):
            tl.connection.close()

    def connection(self):
        if not self.local:
            return self.threadsafe_connection

        return self.batch.destination.connection()

    def use(self):
        self.connection().execute("USE {}".format(self.schema))
