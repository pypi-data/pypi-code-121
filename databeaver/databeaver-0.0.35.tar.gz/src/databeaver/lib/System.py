from .Object import Object
from .PostgreSQL import PostgreSQL
from .MySQL import MySQL
from .Table import Table


class System(Object):
    def __init__(self, type, host, database, user, password):
        """

        :param type:
        :param database:
        :param user:
        :param password:
        """

        # Call Object.__init__()
        super().__init__()

        # Instantiate class variables
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._type = type
        self.actual = None
        self.logger = self.get_logger()

        # Instantiate the database class we have selected
        if self._type == "PostgreSQL":
            self.actual = PostgreSQL(self._host, self._database, self._user, self._password)
        elif self._type == "MySQL":
            self.actual = MySQL(self._host, self._database, self._user, self._password)
        else:
            self.logger.error(f"{self._type} is an invalid system type.")

    def create(self, schema=None, object_to_create=None):
        """
        Create a given Object in the database (withing the given schema
        :param schema:
        :param object_to_create: something we wish to create (Table, Tables, etc)
        :return:
        """
        self.logger.info(f'Creating {object_to_create} in the schema {schema}')
        if object_to_create is None:
            return

        if isinstance(object_to_create, Table):
            self.logger.info(f'Creating table {object_to_create} in the schema {schema}')
            self.actual.create_table(schema, object_to_create.name, object_to_create.columns)
