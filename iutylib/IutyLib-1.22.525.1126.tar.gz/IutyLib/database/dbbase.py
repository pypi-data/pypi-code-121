from IutyLib.database.exceptions import *
from abc import abstractmethod
import datetime

class DataBaseParam:
    host = None
    user = None
    password = None
    dbname = None
    
    def __init__(self,host,user,password,dbname,port=3306):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.dbname = dbname
    
    pass

class Column:
    AutoIncrement = False
    PrimaryKey = False
    IsIndex = False
    UnionIndex = False
    IsUnique = False
    NullAble = True
    Length = None
    Default = None
    Enum = []
    
    Type = int
    
    def __init__(self,**kwargs):
        if 'AutoIncrement' in kwargs:
            self.AutoIncrement = kwargs['AutoIncrement']
        if 'NullAble' in kwargs:
            self.NullAble = kwargs['NullAble']
        if 'PrimaryKey' in kwargs:
            self.PrimaryKey = kwargs['PrimaryKey']
            if self.PrimaryKey:
                self.NullAble = False
        if 'IsIndex' in kwargs:
            self.IsIndex = kwargs['IsIndex']
        if 'UnionIndex' in kwargs:
            self.UnionIndex = kwargs['UnionIndex']
        if 'IsUnique' in kwargs:
            self.IsUnique = kwargs['IsUnique']
        if 'Length' in kwargs:
            self.Length = kwargs['Length']
        if 'Default' in kwargs:
            self.Default = kwargs['Default']
        if 'Enum' in kwargs:
            self.Enum = kwargs['Enum']
        if 'Type' in kwargs:
            self.Type = kwargs['Type']
    
    def getType(self):
        if not self.Length == None:
            length = str(self.Length)
        
        if self.Type == int:
            if self.Length == None:
                length = "11"
            return "int" + "(" + length + ")"
        
        if self.Type == float:
            return "float"
        if self.Type == str:
            if self.Length == None:
                length = "255"
            t = "varchar" + "(" + length + ")"
            if len(self.Enum) > 0:
                t = "enum("
                enumstr = ""
                for e in self.Enum:
                    if len(enumstr) > 0:
                        enumstr += ','
                    enumstr += ("\'" + e + "\'")
                t += enumstr
                t += ")"
                
            
            return t
        if self.Type == datetime.date:
            return "date"
        if (self.Type == datetime.timedelta) | (self.Type == datetime.time):
            if self.Length == None:
                length = "6"
            return "time" + "(" + length + ")"
        if self.Type == datetime.datetime:
            if self.Length == None:
                length = "6"
            return "datetime" + "(" + length + ")"
        if self.Type == bytes:
            if self.Length == None:
                length = "255"
            return "varchar" + "(" + length + ")"
    
    def getSqlStr(self):
        colstr = ""
        
        colstr += (" " + self.getType())
        if self.PrimaryKey:
            colstr += " primary key"
            self.NullAble = False
        if not self.NullAble:
            colstr += " not null"
        
        if (self.Default is None) & (self.NullAble):
            colstr += " default NULL"
        
        if not self.Default is None:
            colstr += (" Default" + '\'' + self.Default + '\'')
        
        if self.AutoIncrement:
            colstr += " AUTO_INCREMENT"
        return colstr
    pass

class SqlDataBase(DataBaseParam):
    _db = None
    
    
    def __init__(self,host,user,password,dbname,port=3306,**kwargs):
        DataBaseParam.__init__(self,host,user,password,dbname,port)
        self.Model = self.getModel.__call__()
        self._dbname = dbname
        
        pass
    
    def getModel(self):
        class Model:
            _db = self
            
            def getColumns(self):
                columns = {}
                for item in self.__class__.__dict__:
                    if self.__class__.__dict__[item].__class__ == Column:
                        columns[item] = self.__class__.__dict__[item]
                return columns
            
            def getDBColumns(self):
                tablename = self.__class__.__name__
                return self._db.getColumnDefine(tablename)
            
            def checkColumn(self):
                columns = self.getColumns()
                dbcolumns = self.getDBColumns()
                
                for col in columns:
                    if col.startswith('_'):
                        continue
                    column = columns[col]
                    checkok = False
                    for dbcolumn in dbcolumns:
                        
                        if dbcolumn['column_name'] == col:
                            
                            if column.getType() != dbcolumn['COLUMN_TYPE']:
                                self._db.alterColumn(self.__class__.__name__,col,column.getSqlStr())
                                checkok = True
                                continue
                            nullable = 'YES'
                            if not column.NullAble:
                                nullable = 'NO'
                            
                            if nullable != dbcolumn['IS_NULLABLE']:
                                self._db.alterColumn(self.__class__.__name__,col,column.getSqlStr())
                                checkok = True
                                continue
                            
                            checkok = True
                            continue
                    if not checkok:
                        #print(col)
                        self._db.addColumn(self.__class__.__name__,col,column.getSqlStr())
                    
            
            def check(self,**kwargs):
                self.creat()
                self.checkColumn()
                pass
            
            def creat(self,**kwargs):
                if self._db.isTableExists(self.__class__.__name__):
                    return
                kwargs['table'] = self.__class__.__name__.lower()
                columns = self.getColumns()
                for column in columns:
                    if not 'columns' in kwargs:
                        kwargs['columns'] = {}
                    kwargs['columns'][column] = columns[column]
                data = self._db.excuteCreat.__call__(**kwargs)
                return data
            
            def query(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteQuery.__call__(**kwargs)
                return data
            
            def add(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteAdd.__call__(**kwargs)
                return data
            
            def replace(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteReplace.__call__(**kwargs)
                return data
            
            def delete(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteDelete.__call__(**kwargs)
                return data
            
            def update(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteUpdate.__call__(**kwargs)
                return data
            
            def drop(self,**kwargs):
                kwargs['table'] = self.__class__.__name__.lower()
                data = self._db.excuteDrop.__call__(**kwargs)
                return data
            
            def tables(self,**kwargs):
                data = self._db.excuteTableInfo.__call__(**kwargs)
                return data
        return Model
    
    
    
    def isTableExists(self,tablename):
        sqlstr = "select table_name  from information_schema.tables where table_schema=\'"
        
        sqlstr += self.dbname
        sqlstr += '\' and table_type=\'base table\''
        sqlstr += ' and table_name ='
        sqlstr += (" \'" + tablename + "\'")
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        if len(data) > 0:
            return True
        return False
    
    def getColumnDefine(self,tablename):
        sqlstr = "select column_name,COLUMN_TYPE,COLUMN_KEY,IS_NULLABLE from information_schema.columns where table_schema= "
        sqlstr += ("\'" + self.dbname + "\'")
        sqlstr += " and table_name = "
        sqlstr += ("\'" + tablename + "\'")
        
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def alterColumn(self,tablename,columnname,alterstr):
        sqlstr = "alter table"
        sqlstr += (' `' + tablename + '`')
        sqlstr += " Modify Column"
        sqlstr += (' `' + columnname + '`')
        sqlstr += (' ' + alterstr)
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def addColumn(self,tablename,columnname,alterstr):
        sqlstr = "alter table"
        sqlstr += (' `' + tablename + '`')
        sqlstr += " Add Column"
        sqlstr += (' `' + columnname + '`')
        sqlstr += (' ' + alterstr)
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteCreat(self,**kwargs):
        sqlstr = "CREATE TABLE "
        if not 'table' in kwargs:
            raise TableError('Creat Has No Table')
        sqlstr += ("`" + kwargs['table'] + "`")
        if not 'columns' in kwargs:
            raise TableError('Creat Has No Column')
        colstr = ""
        indexstr = ""
        unionindexstr = ""
        for col in kwargs['columns']:
            colobj = kwargs['columns'][col]
            if len(colstr) > 0:
                colstr += ','
            colstr += ("`" + col + "`")
            colstr += colobj.getSqlStr()
            if colobj.IsIndex:
                if not colobj.UnionIndex:
                    indexstr += ("," + "Index" + " " + "`" + col + "`" + " " + "(`" + col + "`)")
                else:
                    if len(unionindexstr) > 0:
                        unionindexstr += ","
                    unionindexstr += ("`" + col + "`")
        if len(unionindexstr) > 0:
            unionindexstr = "," + "Index" + " " + "`union`" + " " + "(" + unionindexstr + ")"
            
        sqlstr += ("(" + colstr + indexstr + unionindexstr +")")
        
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
        
    
    def excuteDrop(self,**kwargs):
        sqlstr = "DROP TABLE"
        if not 'table' in kwargs:
            raise TableError('Drop Has No Table')
        sqlstr += ("`" + kwargs['table'] + "`")
        
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteTableInfo(self,**kwargs):
        sqlstr = "SELECT TABLE_NAME FROM information_schema.TABLES where Table_SCHEMA = '{0}'".format(self._dbname)
        if 'orderby' in kwargs:
            sqlstr += (" " + "order by" + " " + kwargs['orderby'])
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
            
    
    @abstractmethod
    def connect(self):
        pass
    
    def excuteSql(self,sqlstr):
        dbx = self.connect()
        db0 = dbx.cursor(self._db.cursors.DictCursor)
        db0.execute(sqlstr)
        db0.close()
        dbx.close()
        return db0

    def excuteQuery(self,**kwargs):
        sqlstr = "select "
        target = '*'
        if 'target' in kwargs:
            target = kwargs['target']
        sqlstr += (target + ' ')
        if not 'table' in kwargs:
            raise QueryError('Query Has No Table')
        sqlstr += ('from ' + "`" + kwargs['table'] + "`" + ' ')
        if 'join' in kwargs:
            sqlstr += (kwargs['join'] + ' ')
        if 'where' in kwargs:
            sqlstr += ("where " + kwargs['where'] + ' ')
        if 'groupby' in kwargs:
            sqlstr += ("group by " + kwargs['groupby'] + ' ')
        if 'orderby' in kwargs:
            sqlstr += ("order by " + kwargs['orderby'] + ' ')
        #Having here
        if 'limit' in kwargs:
            sqlstr += ("limit " + kwargs['limit'] + ' ')
        
        #log here
        #print(sqlstr)
        
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteAdd(self,**kwargs):
        sqlstr = 'insert into '
        if not 'table' in kwargs:
            raise AddError('Add Has No Table')
        sqlstr += ("`" + kwargs['table'] + "`")
        if not 'value' in kwargs:
            raise AddError('Add Has No Value')
        fields = ""
        values = ""
        firstvalue = kwargs['value'].pop(0)
        for v in firstvalue:
            if len(fields) > 0:
                fields+=","
                values+=","
            fields += r"`{}`".format(v)
            if firstvalue[v] == None:
                values += 'null'
            else:
                values += '\'{0}\''.format(firstvalue[v])
        sqlstr += ("(" + fields + ") ")
        sqlstr += "values "
        sqlstr += ("(" + values + ")")
        
        for val in kwargs['value']:
            values = ''
            for v in val:
                if len(values)>0:
                    values+=","
                
                if val[v] == None:
                    values += 'null'
                else:
                    values += '\'{0}\''.format(val[v])
            sqlstr += (",(" + values + ")")
        
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteReplace(self,**kwargs):
        sqlstr = 'replace into '
        if not 'table' in kwargs:
            raise AddError('Add Has No Table')
        sqlstr += ("`" + kwargs['table'] + "`")
        if not 'value' in kwargs:
            raise AddError('Add Has No Value')
        fields = ""
        values = ""
        firstvalue = kwargs['value'].pop(0)
        for v in firstvalue:
            if len(fields) > 0:
                fields+=","
                values+=","
            fields += r"`{}`".format(v)
            if firstvalue[v] == None:
                values += 'null'
            else:
                values += '\'{0}\''.format(firstvalue[v])
        sqlstr += ("(" + fields + ") ")
        sqlstr += "values "
        sqlstr += ("(" + values + ")")
        
        for val in kwargs['value']:
            values = ''
            for v in val:
                if len(values)>0:
                    values+=","
                if val[v] == None:
                    values += 'null'
                else:
                    values += '\'{0}\''.format(val[v])
            sqlstr += (",(" + values + ")")
        
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteDelete(self,**kwargs):
        sqlstr = "delete from "
        if not 'table' in kwargs:
            raise DeleteError('Delete Has No Table')
        sqlstr += (kwargs['table'] + ' ')
        if 'where' in kwargs:
            sqlstr += ("where " + kwargs['where'])
        #log here

        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
    
    def excuteUpdate(self,**kwargs):
        sqlstr = "update "
        if not 'table' in kwargs:
            raise DeleteError('Update Has No Table')
        sqlstr += (kwargs['table'] + ' ')
        if not 'value' in kwargs:
            raise DeleteError('Update Has No Value')
        sqlstr += "set "
        setstr = ""
        for val in kwargs['value']:
            for v in val:
                
                if len(setstr) > 0:
                     setstr += ','
                if val[v] == None:
                    
                    setstr += r"`{}` = null".format(v)
                else:
                    setstr += r"`{}` = '{}'".format(v,val[v])
    
            sqlstr += setstr
    
        if 'where' in kwargs:
            sqlstr += (" where " + kwargs['where'])
        #log here
        #print(sqlstr)
        db0 = self.excuteSql(sqlstr)
        data = []
        for d in db0:
            data.append(d)
        return data
