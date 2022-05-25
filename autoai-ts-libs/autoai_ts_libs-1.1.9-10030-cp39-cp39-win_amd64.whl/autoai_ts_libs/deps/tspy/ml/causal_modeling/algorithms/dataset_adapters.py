import bz2
import pickle
import os

import numpy as np
import pandas as pd

from autoai_ts_libs.deps.tspy.time_series import time_series
from autoai_ts_libs.deps.tspy.ml.causal_modeling.algorithms.datamodel import tes

    

class Data(tes):
    def __init__(self):
        super(tes, self).__init__()
    
    def set_variable_names(self, variable_names):
        self._datadict['variable_names'] = variable_names
        
    def get_variable_names(self):
        return self._datadict['variable_names']
    
    def set_feature_names_dict(self, feature_names_dict):
        self._datadict['feature_names_dict'] = feature_names_dict
        
    def get_feature_names_dict(self):
        return self._datadict['feature_names_dict']
    
    def set_event_type_names(self, event_type_names):
        self._datadict['event_type_names'] = event_type_names
        
    def get_event_type_names(self):
        return self._datadict['event_type_names']
    
    # utility methods
    def to_dataframe(self, ts_column='timestamp', value_column='value'):
        dataframe = pd.DataFrame()
        dataframe[ts_column]    = self.get_ts().squeeze()
        dataframe[value_column] = self.get_eid().squeeze()
        return dataframe
    
    def to_array(self):
        array = self.to_dataframe().to_numpy(dtype = np.dtype(object))
        return array
    
    def to_array_tuple(self):
        array = self.to_array()
        array_tuple = array[:, 0], array[:, 1]
        return array_tuple
    
    def to_timestamped_event_sequence(self, ts_column='timestamp', value_column='value'):
        dataframe = self.to_dataframe(ts_column, value_column)
        
        timestamped_event_sequence = tes()
        timestamped_event_sequence.set_ts(dataframe[ts_column].to_numpy())
        timestamped_event_sequence.set_eid(dataframe[value_column].to_numpy())
        
        return timestamped_event_sequence
    
    def to_timeseries(self,
                      ts_column='timestamp',
                      value_column='value',
                      scaling_factor=None):
        
        if scaling_factor is None:
            scaling_factor = self.to_timeseries_scaling_factor(ts_column, value_column)
        
        dataframe = self.to_dataframe(ts_column, value_column)
        scaled_dataframe = dataframe.copy()
        scaled_dataframe[ts_column] = scaled_dataframe[ts_column].apply(lambda x: scaling_factor * x)
        scaled_dataframe = scaled_dataframe.astype(dtype={ts_column : 'int64'})
        timeseries = time_series(scaled_dataframe, ts_column=ts_column, value_column=value_column)
        return timeseries


    def to_timeseries_scaling_factor(self, ts_column='timestamp', value_column='value'):
        # XXX
        # Consider scaling by the inverse of the minimum distance between
        # successive floating point time values.
        scaling_factor = 1000
        
        return scaling_factor
        



class Dataset:
    def __init__(self):
        self._dataset_dict = {}
        self.keys = []
        
    def __setitem__(self, key, data):
        self._dataset_dict[key] = data
        self.keys.append(key)
    
    def __getitem__(self, key):
        return self._dataset_dict[key]
    
    def get_keys(self):
        return self.keys
    
    def get_size(self):
        return len(self.keys)


    
class Sparse5Dataset(Dataset):
    def __init__(self, root):
        super(Sparse5Dataset, self).__init__()
        
        fpath = os.path.join(root, 'Sparse5.pickle.bz2') 
        with bz2.open(fpath) as f:
            raw_data_list = pickle.load(f)
        size = len(raw_data_list)
        self.raw_data_list = raw_data_list
        self.size          = size
        self._populate()
        
    def _populate(self):
        
        event_type_names = []
        variable_names   = []
        for key, raw_data in enumerate(self.raw_data_list):
            data = Data()
            
            event_type_names = sorted(list(set(raw_data['et'])))
            variable_names   = event_type_names
            data.set_event_type_names(event_type_names)
            
            data.set_variable_names(variable_names)
            
            data.set_ts(raw_data['ts'])
            data.set_eid(raw_data['et'])
            self[key] = data
  


class Dense10Dataset(Dataset):
    def __init__(self, root):
        super(Dense10Dataset, self).__init__()
        
        fpath = os.path.join(root, 'Dense10.pickle.bz2') 
        with bz2.open(fpath) as f:
            raw_data = pickle.load(f)
        size = 1
        self.raw_data_list = [raw_data]
        self.size          = size
        self._populate()
        
    def _populate(self):
        
        event_type_names = []
        variable_names   = []
        for key, raw_data in enumerate(self.raw_data_list):
            data = Data()
            
            event_type_names = sorted(list(set(raw_data['temporalEvents']['etype'])))
            variable_names   = event_type_names
            data.set_event_type_names(event_type_names)
            
            data.set_variable_names(variable_names)
            
            data.set_ts(raw_data['temporalEvents']['ts'])
            data.set_eid(raw_data['temporalEvents']['etype'])
            self[key] = data


    
class CloudDataset(Dataset):
    def __init__(self, root):
        super(CloudDataset, self).__init__()
        
        fpath = os.path.join(root, 'cloud.pickle.bz2') 
        with bz2.open(fpath) as f:
            raw_data = pickle.load(f)
        size = 1
        self.raw_data_list = [raw_data]
        self.size          = size
        self._populate()
        
    def _populate(self):
    
        event_type_names = []
        variable_names   = []
        for key, raw_data in enumerate(self.raw_data_list):
            data = Data()
            
            event_type_names = sorted(list(set(raw_data['eventtypes'])))
            variable_names   = event_type_names
            data.set_event_type_names(event_type_names)
            
            data.set_variable_names(variable_names)
            
            data.set_ts(raw_data['timestamp'])
            data.set_eid(raw_data['eventtypes'])
            self[key] = data




class ClaranetDataset(Dataset):
    def __init__(self, root):
        super(ClaranetDataset, self).__init__()
        
        fpath = os.path.join(root, 'data_Claranet.pickle.bz2') 
        with bz2.open(fpath) as f:
            _raw_data = pickle.load(f)
        
        # First of all we should sort the time stamp
        data = _raw_data.drop_duplicates().sort_values(by=['FIRSTOCCURRENCE'])
        
        # Generic failure processing time
        ts= data['FIRSTOCCURRENCE']/1000.
        
        #===================
        # Georgios filtering --------
        tstart = pd.to_datetime('2015-01-01').timestamp()
        tend = pd.to_datetime('2015-07-01').timestamp()
        mask = (data['ENTITYTYPE']=='Router') & (data['NMOSCAUSETYPE'] != 0)            & (data['FIRSTOCCURRENCE']/1000 >= tstart)            & (data['FIRSTOCCURRENCE']/1000 <= tend)
        
        DF = data.loc[mask,:]
        DF.reset_index(drop=True)
        
        # pulling event types and exclude the event types occuring too few
        eventTypes = DF['EVENTID']
        Nmin = 10
        counts = eventTypes.value_counts()
        deleteEventTypeSet = set(counts.index[counts <=Nmin])
        mask = np.array([eventTypes.iloc[ii] in deleteEventTypeSet                 for ii in range( len(eventTypes) ) ])
        DF = DF.loc[~mask,:]
        DF.reset_index(drop=True)
        N = DF.shape[0]
        # print('{} events found'.format(N))          
        
        # Computng some stats of this data
        eventType = np.array(DF['EVENTID'])
        ts = np.array(DF['FIRSTOCCURRENCE'])/1000.
        
        raw_data = {
            'timestamps' : ts, 
            'eventtypes' : eventType,
            'dataframe'  : DF
        }
        size = 1
        self.raw_data_list = [raw_data]
        self.size          = size
        self._populate()
        

    def _populate(self):
    
        event_type_names = []
        variable_names   = []
        for key, raw_data in enumerate(self.raw_data_list):
            data = Data()
            
            event_type_names = sorted(list(set(raw_data['eventtypes'])))
            variable_names   = event_type_names
            data.set_event_type_names(event_type_names)
            
            data.set_variable_names(variable_names)
            
            data.set_ts(raw_data['timestamps'])
            data.set_eid(raw_data['eventtypes'])
            self[key] = data



class Claranet4KSubsetDataset(Dataset):
    def __init__(self, root):
        super(Claranet4KSubsetDataset, self).__init__()
        
        fpath = os.path.join(root, 'Claranet_4K_subset.pickle.bz2') 
        with bz2.open(fpath) as f:
            raw_data = pickle.load(f)
        size = 1
        self.raw_data_list = [raw_data]
        self.size          = size
        self._populate()
        
    def _populate(self):
    
        event_type_names = []
        variable_names   = []
        for key, raw_data in enumerate(self.raw_data_list):
            data = Data()
            
            event_type_names = sorted(list(set(raw_data['event_types'])))
            variable_names   = event_type_names
            data.set_event_type_names(event_type_names)
            
            data.set_variable_names(variable_names)
            
            data.set_ts(raw_data['timestamps'])
            data.set_eid(raw_data['event_types'])
            self[key] = data

