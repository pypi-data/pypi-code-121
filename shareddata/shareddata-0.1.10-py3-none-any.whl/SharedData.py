import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

from SharedData.Logger import Logger
from SharedData.SharedDataFeeder import SharedDataFeeder
from SharedData.Metadata import Metadata
from SharedData.SharedDataRealTime import SharedDataRealTime

class SharedData:
    
    def __init__(self, database, mode='rw', sync_frequency_days=0.5, user='master'):
        if Logger.log is None:            
            Logger('SharedData')
        
        Logger.log.debug('Initializing SharedData %s,%s,%s ...' % (user,database,mode))
        
        self.database = database
        self.sync_frequency_days = sync_frequency_days
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

        if (Logger.user!='master') & (user=='master'):
            self.s3write=False
            mode = 'r'
        
        self.mode = mode
                
        # last download sync datetime
        self.lastsync = pd.DataFrame([])
        self.lastsyncfpath = Path(os.environ['DATABASE_FOLDER']) / (user + '/'+ database + '/lastsync.txt')
        if self.lastsyncfpath.is_file():
            self.lastsync = pd.read_csv(self.lastsyncfpath)
            self.lastsync = self.lastsync.set_index('file')
            self.lastsync['timestamp'] = pd.to_datetime(self.lastsync['timestamp'])

        # DATA DICTIONARY
        # SharedDataTimeSeries: data[feeder][period][tag] (date x symbols)
        # SharedDataFrame: data[feeder][period][date] (symbols x tags)
        self.data = {} 

        # Symbols collections metadata
        self.metadata = {}

        # DATASET        
        self.dataset_metadata = Metadata('DATASET/' + database,\
            mode=mode,sync_frequency_days=sync_frequency_days,\
            user=self.user)
        self.dataset = self.dataset_metadata.static
        
        Logger.log.debug('Initializing SharedData %s,%s,%s DONE!' % (user,database,mode))

    def __setitem__(self, feeder, value):
        self.data[feeder] = value
                
    def __getitem__(self, feeder):        
        if not feeder in self.data.keys():
            self.data[feeder] = SharedDataFeeder(self, feeder)
        return self.data[feeder]

    def getMetadata(self, collection):
        if not collection in self.metadata.keys():              
            self.metadata[collection] = Metadata(collection,\
                mode=self.mode,sync_frequency_days=self.sync_frequency_days,\
                user=self.user)
        return self.metadata[collection]

    def getSymbols(self, collection):        
        return self.getMetadata(collection).static.index.values
  
    def SubscribeRealTime(self):
        SharedDataRealTime.Subscribe(self)