from peewee import SqliteDatabase


class BasePeewee(object):

    def __init__(self):
        self.db = None

    def connent_sqlite(self, path):
        self.db = SqliteDatabase(path)
        return self.db
