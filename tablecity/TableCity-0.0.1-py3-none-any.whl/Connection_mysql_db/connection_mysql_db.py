from peewee import *

db = MySQLDatabase(None)


class ConnectionMySql:
    
    def connection_db(database: str, user: str, password: str, host: str):
        '''It is necessary to fill in data for authorization in the database.'''
        
        db.init(database, user=user, password=password, host=host) 