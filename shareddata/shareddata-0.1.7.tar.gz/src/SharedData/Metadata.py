import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import numpy as np
import time
import subprocess
from datetime import datetime, timedelta

from SharedData.Logger import Logger
from SharedData.SharedDataAWSS3 import S3SyncDownloadMetadata,S3Upload

class Metadata():
    
    def __init__(self, name, mode='rw', sync_frequency_days=0.5, user='master'):
        if Logger.log is None:
            Logger('Metadata')

        Logger.log.debug('Initializing Metadata %s,%s,%s ...' % (user,name,mode))
        self.user = user
        
        self.s3read = False
        self.s3write = False
        if mode == 'r':
            self.s3read = True
            self.s3write = False
        elif mode == 'w':
            self.s3read = False
            self.s3write = True
        elif mode == 'rw':
            self.s3read = True
            self.s3write = True        

        self.name = name
        self.xls = {}
        self.static = pd.DataFrame([])        
        self.symbols = pd.DataFrame([],dtype=str)
        self.series = pd.Series([],dtype=str)
        self.fpath = Path(os.environ['DATABASE_FOLDER']) / user

        self.pathxls = self.fpath /  ('Metadata/'+name+'.xlsx')
        self.pathpkl = self.fpath /  ('Metadata/'+name+'.pkl')
        self.pathsymbols = self.fpath /  ('Metadata/'+name+'_SYMBOLS.pkl')
        self.pathseries = self.fpath /  ('Metadata/'+name+'_SERIES.pkl')

        if (self.s3read):

            self.lastsync = pd.DataFrame([])
            self.lastsyncfpath = Path(os.environ['DATABASE_FOLDER']) / (user+'/Metadata/lastsync.txt')
            if self.lastsyncfpath.is_file():
                self.lastsync = pd.read_csv(self.lastsyncfpath)
                self.lastsync = self.lastsync.set_index('file')
                self.lastsync['timestamp'] = pd.to_datetime(self.lastsync['timestamp'])

            now = datetime.utcnow()
            sync = False
            if not self.name in self.lastsync.index:
                sync = True
            else:
                td = (now - self.lastsync['timestamp'][self.name]).seconds/86400
                if td>sync_frequency_days:
                    sync = True

            if sync:
                if S3SyncDownloadMetadata(self.pathpkl,self.name):
                    self.lastsync.loc[self.name,'timestamp'] = now
                    self.lastsync.index.name = 'file'
                    self.lastsync.to_csv(self.lastsyncfpath)       

        # prefer read pkl
        # but read excel if newer
        readpkl = self.pathpkl.is_file()
        readxlsx = self.pathxls.is_file()
        if (readpkl) & (readxlsx):
            readxlsx = os.path.getmtime(self.pathxls)>os.path.getmtime(self.pathpkl)
            readpkl = not readxlsx
        
        if readpkl:
            tini = time.time()
            Logger.log.debug('Loading metadata pkl ' + name + ' ...')
            self.static = pd.read_pickle(self.pathpkl)
            self.static = self.static.sort_index()
            if self.pathsymbols.is_file():
                self.symbols = pd.read_pickle(self.pathsymbols)
                self.symbols = self.symbols.sort_index()
            if self.pathseries.is_file():
                self.series = pd.read_pickle(self.pathseries)
                self.series = self.series.sort_index()
            Logger.log.debug('Loading metadata pkl %s %.2f done!' % (name,time.time()-tini))

        elif readxlsx:
            tini = time.time()
            Logger.log.debug('Loading metadata xlsx ' + name + ' ...')
            self.xls = pd.read_excel(self.pathxls,sheet_name=None)
            self.static = self.xls['static']
            if 'symbols' in self.xls.keys():
                self.symbols = self.xls['symbols']
            if not self.static.empty:
                self.static = self.static.set_index(self.static.columns[0])
            if not self.symbols.empty:
                self.symbols = self.symbols.set_index(self.symbols.columns[0])
            Logger.log.debug('Loading metadata xlsx %s %.2f done!' % (name,time.time()-tini))
        
        Logger.log.debug('Initializing Metadata %s,%s DONE!' % (name,mode))

    def save(self,save_excel=False):
        tini = time.time()
        Logger.log.debug('Saving metadata ' + self.name + ' ...')  
        if not os.path.isdir(self.pathpkl.parents[0]):
            os.makedirs(self.pathpkl.parents[0])                   

        # save excel first so that last modified
        # timestamp is older        
        if save_excel:
            writer = pd.ExcelWriter(self.pathxls, engine='xlsxwriter')            
            self.static.to_excel(writer,sheet_name='static')        
            if not self.symbols.empty:
                self.symbols.to_excel(writer,sheet_name='symbols')
            writer.save()        
            if self.s3write:
                S3Upload(self.pathxls)

        self.static.to_pickle(self.pathpkl)
        if self.s3write:
            S3Upload(self.pathpkl)

        if not self.symbols.empty:
            self.symbols.to_pickle(self.pathsymbols)
            if self.s3write:
                S3Upload(self.pathsymbols)

        if not self.series.empty:
            self.series.to_pickle(self.pathseries)
            if self.s3write:
                S3Upload(self.pathseries)


        Logger.log.debug('Saving metadata ' + self.name + \
            ' %.2f done!' % (time.time()-tini))
    
    def mergeUpdate(self,newdf):
        ddidx = newdf.index.duplicated()
        if ddidx.any():
            newdf = newdf[~newdf.index.duplicated(keep='first')]
            Logger.log.warning('Metadata merge duplicated index for new dataframe!')
        ddidx = self.static.index.duplicated()
        if ddidx.any():
            self.static = self.static[~self.static.index.duplicated(keep='first')]
            Logger.log.warning('Metadata merge duplicated index for static dataframe!')
        newcolsidx = ~newdf.columns.isin(self.static.columns)
        if newcolsidx.any():
            newcols = newdf.columns[newcolsidx]
            for c in newcols:
                self.static.loc[:,c] = newdf[c]                
        newidx = ~newdf.index.isin(self.static.index)
        if newidx.any():
            self.static = self.static.reindex(index=self.static.index.union(newdf.index))
        newcol = ~newdf.columns.isin(self.static.columns)
        if newcol.any():
            self.static = self.static.reindex(columns=self.static.columns.union(newdf.columns))
        self.static.update(newdf)
