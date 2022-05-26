#  Copyright (C) 2021 Vremsoft LLC and/or its subsidiary(-ies).
#  All rights reserved.
#  Contact: Laura Chapman  (edc@vremsoft.com)
#  Commercial Usage
#  Licensees holding valid Vremsoft LLC licenses may use this file in
#  accordance with the License Agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in
#  a written agreement between you and Vremsoft. LLC
#

import math
import argparse

from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class VremMYSqlRecord:
    def __init__(self, timeOf=QDateTime, d=None):
        self._timeOf = timeOf
        self._data = d


class Stats:
    def __init__(self, Val=None):
        if Val != None:
            self.N = Val.N
            self.Sum = Val.Sum
            self.SumSq = Val.SumSq
            self.Begin = Val.Begin
            self.Highest = Val.Highest
            self.Lowest = Val.Lowest
        else:
            self.N = 0
            self.Sum = 0.0
            self.SumSq = 0.0
            self.Begin = True
            self.Highest = 0
            self.Lowest = 0

    def Add(self, X, NoZ=True):
        if X != None:
            if X != 0 or (X == 0 and NoZ == False):
                self.N = self.N + X
                self.Sum = self.Sum + X
                self.SumSq = self.SumSq + (X * X)
                if self.Begin:
                    self.Begin = False
                    self.Highest = X
                    self.Lowest = X

                else:
                    if X > self.Highest:
                        self.Highest = X
                    if X < self.Lowest:
                        self.Lowest = X

    def GetMean(self):
        if self.N:
            return self.Sum / self.N
        return 0

    def GetStd(self):
        if self.N > 1:
            math.sqrt((self.SumSq - ((self.Sum * self.Sum) / self.N)) / (self.N - 1))
        return 0

    def GetLowest(self):
        return self.Lowest

    def GetHighest(self):
        return self.Highest

    def Reset(self):
        self.N = 0
        self.Sum = 0.0
        self.SumSq = 0.0
        self.Begin = True
        self.Highest = 0
        self.Lowest = 0


class CDStats:
    def __init__(self, ignorZ=True):
        self.IgnorZ = ignorZ
        self.stats = Stats

    def Reset(self):
        self.stats.Reset()

    def GetSigma(self):
        return self.stats.GetStd()

    def GetMean(self):
        return self.stats.GetMean()

    def GetHighest(self):
        return self.Highest_Value

    def GetWhereHigestHappened(self):
        return self.Highest_Position

    def GetLowest(self):
        return self.Lowest_Value

    def GetWhereLowestHappened(self):
        return self.Lowest_Position

    def Computer(self, records=[]):
        begin = True
        for i in range(0, len(records)):
            self.stats.Add(records[i], self.IgnorZ)


class DateTime:
    def __init__(self, dateTime=None):
        if dateTime == None:
            self.dateTime = QDateTime.currentDateTime()
        else:
            self.dateTime = QDateTime.fromString(dateTime, "yyyy MM dd hh:mm:ss")

    def SetDateTime(self, dateTime):
        self.dateTime = QDateTime.fromString(dateTime, "yyyy MM dd hh:mm:ss")

    def GetLocalDateTimeStr(self):
        return self.dateTime.toString("yyyy MM dd hh:mm:ss")

    def GetLocalDataTime(self):
        return self.dateTime


class stdsql():
    def __init__(self, user="vremsoft", database="vremsoft", hostname="localhost", port=5432, password="vrem2010!"):
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setDatabaseName(database)
        self.db.setHostName(hostname)
        self.db.setPort(int(port))
        self.db.setPassword(password)
        self.db.setUserName(user)
        self.db.setConnectOptions("connect_timeout=5")
        self.db.open()
        # In case driver not loaded, here gives hint
        print(self.db.lastError().text())
        self.database = database
        self.tableName = self.database + "_trendtable"
        self.sub_mode = QSqlTableModel()
        self.sub_mode.setTable(self.tableName)
        self.sub_mode.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.sub_mode.select()

    def ConvertToQVariantList(self, stream):
        var = QDataStream(stream, QIODevice.ReadWrite)
        var.setVersion(QDataStream.Qt_5_0)
        var.setByteOrder(QDataStream.LittleEndian)
        return var.readQVariantList()

    def getTableFromSub(self, sub):
        query = QSqlQuery(self.db)
        select = "SELECT  * FROM  " + self.database + "_trendtable where id_subscriber = " + sub + "';"
        if query.exec(select):
            if query.next():
                return query.value(1)
        return ""

    def getAllTracking(self):
        all = {}
        nrows = self.sub_mode.rowCount()
        for i in range(0, nrows):
            rc = self.sub_mode.record(i)
            subcount = rc.count()

            v1 = str(rc.value(0))
            v2 = str(rc.value(1))
            if v1 and v2:
                all.update({v1: v2})
        return all

    def GetLastDataRecordsFromTrendTable(self, table):

        t = table
        end = str(QDateTime.currentDateTimeUtc().toMSecsSinceEpoch() + 1)
        query = QSqlQuery(self.db)
        #      select = "SELECT * FROM " + t + " where id_datetime <= '" + end + "'"
        select = "SELECT * FROM " + t + " order by id_datetime desc limit 1"
        rec = VremMYSqlRecord

        if query.exec(select) and query.last():
            utime_t = query.value(0)
            UTC = QDateTime(QDateTime.currentDateTimeUtc())
            UTC.setMSecsSinceEpoch(utime_t)
            rec._timeOf = UTC.toLocalTime()
            bs = query.value(1)
            rec._data = self.ConvertToQVariantList(bs)

        return rec

    def GetLastDataRecordsFromTrendTableTo(self, table, toLocalTime):
        t = table
        end = str(toLocalTime.toUTC().toMSecsSinceEpoch())

        query = QSqlQuery(self.db)
        select = "SELECT * FROM " + t + " where id_datetime <= '" + end + "'"
        rec = VremMYSqlRecord

        if query.exec(select) and query.last():
            utime_t = query.value(0)
            UTC = QDateTime(QDateTime.currentDateTimeUtc())
            UTC.setMSecsSinceEpoch(utime_t)
            rec._timeOf = QDateTime(UTC.toLocalTime())
            bs = query.value(1)
            rec._data = self.ConvertToQVariantList(bs)

        return rec

    def GetLastDataRecordsFromTrendTableFromTo(self, table, fromLocalTime, toLocalTime):
        t = table
        begin = str(fromLocalTime.toUTC().toMSecsSinceEpoch())
        end = str(toLocalTime.toUTC().toMSecsSinceEpoch())
        query = QSqlQuery(self.db)
        select = "SELECT * FROM " + t + " where id_datetime  >='" + begin + "' and  id_datetime  <='" + end + "'"
        rec = VremMYSqlRecord
        if query.exec(select) and query.last():
            utime_t = query.value(0)
            UTC = QDateTime(QDateTime.currentDateTimeUtc())
            UTC.setMSecsSinceEpoch(utime_t)
            rec._timeOf = QDateTime(UTC.toLocalTime())
            bs = query.value(1)
            rec._data = self.ConvertToQVariantList(bs)

        return rec

    def GetAllDataRecordsFromTrendTable(self, table, fromLocalTime, toLocalTime):
        t = table
        begin = str(fromLocalTime.toUTC().toMSecsSinceEpoch())
        end = str(toLocalTime.toUTC().toMSecsSinceEpoch())
        query = QSqlQuery(self.db)
        select = "SELECT * FROM " + t + " where id_datetime  >= '" + begin + "' and " + " id_datetime  <='" + end + "'"

        lst = []
        if query.exec(select):
            while query.next():
                utime_t = query.value(0)
                UTC = QDateTime(QDateTime.currentDateTimeUtc())
                UTC.setMSecsSinceEpoch(utime_t)

                _timeOf = QDateTime(UTC.toLocalTime())
                _bs = query.value(1)
                _data = self.ConvertToQVariantList(_bs)
                lst.append(VremMYSqlRecord(_timeOf, _data))
        return lst

    def GetAllDataRecordsFromTrendTableAsMatrix(self, table, fromLocalTime, toLocalTime,
                                                format="yyyy.MM.dd hh:mm:ss AP"):
        t = table
        f = QDateTime.fromString(fromLocalTime, format)
        t = QDateTime.fromString(toLocalTime, format)

        r = self.GetAllDataRecordsFromTrendTable(self, table, f, t)

        lst = []
        for j in range(0, len(r)):
            row = []
            rec = r[j]
            te = str(rec._timeOf.toString())
            row.append(te)
            row = row + rec._data
            lst.append(row)

        return lst


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(description="Version 1.5.3 Stec Pjanice Python Version")
    # Add the arguments
    my_parser.add_argument('-d', '--host', metavar='host', required=False)

    args = my_parser.parse_args()
    host = args.host

    if  host is None :
       host = "localhost"


    postgres = stdsql("vremsoft", "vremsoft", host, 5432,"vrem2010!" )
    db = postgres.db
    allie = postgres.getAllTracking()
    print(allie)

    print("................................. Last Value ....................................................")
    for key in allie:
        t = key
        table = allie.get(t, None)
        if table != None:
            rec = postgres.GetLastDataRecordsFromTrendTable(table)
            te = str(rec._timeOf.toString("yyyy MM dd hh:mm:ss"))
            print(t[0], te, ":", rec._data)

    today = QDateTime.currentDateTime()
    before = QDateTime.currentDateTime().addMonths(-1)

    print("................................. All Values ....................................................")

    for key in allie:
        t = key
        table = allie.get(t, None)
        if table != None:
            print(key, "....", table)
            r = postgres.GetAllDataRecordsFromTrendTable(table, before, today)
            for j in range(0, len(r)):
                rec = r[j]
                te = str(rec._timeOf.toString("yyyy MM dd hh:mm:ss"))
                print(key, " : ", table, " : ", t[0], te, " : ", rec._data)
