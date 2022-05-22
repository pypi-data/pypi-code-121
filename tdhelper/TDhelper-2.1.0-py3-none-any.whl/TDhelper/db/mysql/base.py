import mysql.connector.pooling
import threading
class db_pool:
    event= threading.Event()
    def __init__(self, config, m_pool_size= 10):
        self.__pool= mysql.connector.pooling.MySQLConnectionPool(
            pool_size= m_pool_size,pool_reset_session= True, **config)
            
    def getSession(self):
        try:
            if self.__pool:
                return self.__pool.get_connection()
            else:
                return None
        except Exception as e:
            return None