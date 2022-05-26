import pandas as pd
import numpy as np


from SharedData.Logger import Logger
from SharedData.SharedDataPeriod import SharedDataPeriod

class SharedDataFeeder():
    
    def __init__(self, sharedData, feeder):
        self.feeder = feeder
        self.sharedData = sharedData        
    
        self.dataset = sharedData.dataset
        if len(self.dataset)>0:
            idx = self.dataset['feeder']==feeder            
            if np.any(idx):
                self.dataset = self.dataset[idx]
            else:
                self.dataset = pd.DataFrame([]) 
        else:
            Logger.log.warning('feeder %s not found in dataset!' % (self.feeder))
            #raise Exception('feeder not found in dataset!')

        # DATA DICTIONARY
        # data[period][tag]
        self.data = {} 
    
    def __setitem__(self, period, value):
        self.data[period] = value
                
    def __getitem__(self, period):
        if not period in self.data.keys():
            if (period=='D1') | (period=='M15') | (period=='M1'):
                self.data[period] = SharedDataPeriod(self, period)
            else:
                Logger.log.error('Period '+period+ ' not supported!')
                raise ValueError('Period '+period+ ' not supported!')
        return self.data[period]
