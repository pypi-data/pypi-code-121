from IutyLib.database.dbbase import *
import pymysql as mysql
import datetime

class MySql(SqlDataBase):
    def __init__(self,host,user,password,dbname,port=3306,**kwargs):
        SqlDataBase.__init__(self,host,user,password,dbname,port,**kwargs)
        self._db = mysql
    
    def connect(self):
        dbx = self._db.connect(host=self.host, user=self.user,port=self.port,
                                password=self.password, database=self.dbname,
                                charset='utf8')
        dbx.autocommit(True)
        return dbx





if __name__ == '__main__':
    mysql = MySql(host='localhost',port=3306,user='root',password='fastcorp',database='test')
    
    class test(mysql.Model):
        ID = Column(PrimaryKey = True,AutoIncrement = True)
        F = Column(Type=float,IsIndex = True,UnionIndex = True)
        
        S = Column(Type = str,IsIndex = True,UnionIndex = True,Length = 4)
        D = Column(Type = datetime.date,NullAble = True)
        T = Column(Type = datetime.timedelta,NullAble = True)
        #CT = Column(Type = datetime.datetime,NullAble = True)
        DT = Column(Type = datetime.datetime,NullAble = True)
        E = Column(Type = str,Enum = ['e1','e2','e3'],Default = 'e2')
        def __init__(self,name = None):
            if not name is None:
                self.__class__.__name__ = name
        
        pass
    t = test()
    
    s = datetime.datetime.now()
    t.check()
    

    for i in range(300):
        db0 = t.add(value=[{'F' : 3.14*i,'S' : i,'D':datetime.date.today(),'T':datetime.datetime.now()-s,'DT':s}])
        #db0 = t.update(value=[{'F' : 3.14*i,'S' : i,'D':datetime.date.today(),'T':datetime.datetime.now()-s,'CT':s}],where='ID={}'.format(i*2))
    db0 = t.query(orderby = 'ID desc')
    
    #db0 = t.drop()
    
    
    for d in db0:
        print(d)