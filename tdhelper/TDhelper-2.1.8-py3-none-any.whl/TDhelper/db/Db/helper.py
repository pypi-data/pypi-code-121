import os
from TDhelper.db.Db.base import base

m_dbDao=None

def dbInstance(dbPath,dbName):
        if not m_dbDao:
                dbPath=str(os.path.split(os.path.realpath(__file__))[0])+"\\"+dbName
                m_dbDao=base(dbPath)