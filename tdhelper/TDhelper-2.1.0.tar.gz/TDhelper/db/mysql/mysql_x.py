import mysqlx

class mysql_x:
    

    def __init__(self, connection_str, options_str):
        self.__conn_str= None
        self.__options_str= None
        self.clients= None

    def getSession(self):
        if self.clients:
            return self.clients.get_session()

    def createSessionPool(self, connection_str, options_str):
        self.clients= mysqlx.get_client(connection_str, options_str)

    def openDataBase(self, dataBaseName, session):
        if session:
            return session.get_schema(dataBaseName)

    def openTable(self, tableName, schema):
        if schema:
            return schema.get_collection(tableName)

def getConnectionStr(host,port,user,password):
    return {
            'host':host if host else "host.5ker.com",
            'port':port if port else 3308,
            'user':user,
            'password':password
    }

def getPoolOptionsStr(enabled=True,maxSize=1,max_idle_time=0,queue_timeout=0):
    return {
            'pooling':{
            'enabled':enabled,
            'max_size':maxSize,
            'max_idle_time':max_idle_time,
            'queue_timeout':queue_timeout
        }
    }
