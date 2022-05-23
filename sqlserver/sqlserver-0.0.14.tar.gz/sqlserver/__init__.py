# ADGSTUDIOS 2022
import pyodbc
import pandas as pd

class adgsqlserver():
    def __init__(self, connectionstring):
        self.connectionstring = connectionstring

    def fields(self, cur):
        results = {}
        column = 0
        for d in cur.description:
            results[d[0]] = column
            column = column + 1
        return results

    def GetRecordsOfColumn(self, SelectQuery, ColumnName):
        try:
            conn = pyodbc.connect(self.connectionstring)
            cursor = conn.cursor()
            cursor.execute(SelectQuery)
            field_map = self.fields(cursor)
            values = []
            for row in cursor:
                values.append(row[field_map[ColumnName]])
            return values
        except Exception as e:
            print(e)

    def ExecuteQuery(self, Query):
        try:
            conn = pyodbc.connect(self.connectionstring)
            cursor = conn.cursor()
            cursor.execute(Query)
            cursor.commit()
        except Exception as e:
            print(e)

    def GetRecordsAsDict(self, SelectQuery):
        try:
            conn = pyodbc.connect(self.connectionstring)
            cursor = conn.cursor()
            cursor.execute(SelectQuery)
            return {'results':
                    [dict(zip([column[0] for column in cursor.description], row))
                     for row in cursor.fetchall()]}
        except Exception as e:
            print(e)

    def CreateCSVTable(self,csvfile):
            df = pd.read_csv(csvfile)
            tablename = csvfile.split('.')[0]
            payload = ''
            columns = list(df.keys())
            for i,column in enumerate(columns):
                if i == len(columns)-1:
                  payload += ('['+column+']'+' varchar(max)'+'\n')
                else:
                  payload += ('['+column+']'+' varchar(max)'+','+'\n')
                    
            query = f'''
            IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{tablename}' AND TABLE_SCHEMA = 'dbo')
            BEGIN
                DROP TABLE [dbo].[{tablename}]
                CREATE TABLE [dbo].[{tablename}]
                (
                    {payload}
                );
            END
            ELSE
                CREATE TABLE [dbo].[{tablename}]
                (
                    {payload}
                );
            '''
            try:
                conn = pyodbc.connect(self.connectionstring)
                cursor = conn.cursor()
                cursor.execute(query)
                cursor.commit()
                return 'Table Created'
            except Exception as e:
                return e
        
    def InsertCSVData(self,csvfile):
        df = pd.read_csv(csvfile)
        tablename = csvfile.split('.')[0]
        columns = list(df.keys())
        payload = ''
        for index, row in df.iterrows():
            record = '('
            for i,column in enumerate(columns):
                record += "'"+str(row[column]).replace("'"," ")+"'" + ','
            record = record[:-1]
            payload += record+'),'+'\n'

            if index % 1000 == 0:
                query = f'''
                INSERT INTO {tablename}
                VALUES
                {payload[:-2]}
                '''
                try:
                    conn = pyodbc.connect(self.connectionstring)
                    cursor = conn.cursor()
                    cursor.execute(query)
                    cursor.commit()
                except Exception as e:
                    print(e)
                 
                payload = ''

        if len(payload) > 0:
                query = f'''
                INSERT INTO {tablename}
                VALUES
                {payload[:-2]}
                '''
                try:
                    conn = pyodbc.connect(self.connectionstring)
                    cursor = conn.cursor()
                    cursor.execute(query)
                    cursor.commit()
                except Exception as e:
                    print(e)