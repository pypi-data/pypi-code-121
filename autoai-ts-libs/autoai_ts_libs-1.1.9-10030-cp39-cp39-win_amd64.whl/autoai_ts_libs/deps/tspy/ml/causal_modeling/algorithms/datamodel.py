import abc
import sys

# Ensure compatibility with Python 2/3
if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})
    
import numpy as np 

class Inputdata(ABC):
    """
    Base class for input data objects that are consumed by causal algorithms. 
    Causal algorithms included in the toolkit generally accept two types of data objects:
    (a) Multivariate Time series.
    (b) Timestamped event sequence. 
    
    For both above, in the base case, the input data is represented by a datamatrix of form (nsamples, nvariables) where each causal variable
    contributes a scalar feature value per time sample. In the general case, the input data is represented by a datamatrix of form 
    (nsamples, nvariables, nfeatures) where each causal variable can contribute a feature vector per time sample i.e. nfeatures >=1. 
    
    In case of (a), the time stamps are irrelevant and not processed by the algorithms. For e.g. if samples are collected at regular time steps. 
    In case of (b), the time stamps are relevant and are processed by the algoithms. Therefore these are stored. 
    For e.g. if samples are collected at irregular time steps. 
    
    (a) and (b) are implemeted by inherited classes mts and tes respectively. 
    
    The functions create_dm and create_dm3d below are both capable of allocating space for general datamatrices where nfeatures >=1. 
    They only differ in the manner in which data would be stored: (nsamples x nvariables*nfeatures) versus (nsamples x nvariables x nfeatures). 
    Based on how the algorithms consume data, either of these 2 formats may be useful. 
    """
        
    def __init__(self):
        """
        Initialize an empty dictionary of (key, ndarray) pairs
        that holds all data needed by an algorithm
        """
        self._datadict = {}
        self._datadict['dm'] = None
                
    def get_datadict(self):
        """
        returns data dictionary
        """        
        return(self._datadict)
        
    def create_dm(self, nsamples, nvariables, nfeatures=1, dtype=float): 
        """
        allocate space for datamatrix in 2d format (nsamples, nvariables*nfeatures)
        """ 
        self._datadict['dm'] = np.zeros((nsamples, nvariables*nfeatures), dtype=dtype)

    def create_dm3d(self, nsamples, nvariables, nfeatures=1, dtype=float): 
        """
        allocate space for datamatrix in 3d format (nsamples, nvariable, nfeatures)
        """ 
        self._datadict['dm'] = np.zeros((nsamples, nvariables, nfeatures), dtype=dtype)        
        
    def set_dm(self, mat):
        """
        sets datamatrix based in an input ndarray
        """
        self._datadict['dm'] = mat
                        
        
    def get_dm(self):
        """
        Returns the datamatrix
        """        
        return(self._datadict['dm'])
        

        
class tes(Inputdata):
    """
    Base class for Timestamped event sequence(tes) data objects consumed by causal algorithms
    """

    def __init__(self):
        """
        Initialize an empty dictionary that holds all data & timestamps
        """
        super(tes, self).__init__()
        self._datadict['ts'] = None
        
    def create_ts(self, nsamples, dtype=float):
        """
        allocates space for timestamps
        """        
        self._datadict['ts'] = np.zeros((nsamples, 1), dtype=dtype)
        
    def set_ts(self, ts_arr):
        """
        Set timestamps based on list or numpy array
        """                        
        if (type(ts_arr) == list):
            ts_arr = np.array(ts_arr)        
        
        self._datadict['ts'] = ts_arr.reshape(-1, 1)

    def get_ts(self):
        """
        returns timestamps
        """                        
        return(self._datadict['ts'])
    
    def create_eid(self, nsamples, dtype=int):
        """
        allocate space for event ids
        """                                            
        self._datadict['eid'] = np.zeros((nsamples, 1), dtype=dtype)

    def set_eid(self, eid_arr):
        """
        Set event ids based on list or numpy array
        """         
        if (type(eid_arr) == list):
            eid_arr = np.array(eid_arr)
        
        self._datadict['eid'] = eid_arr.reshape(-1, 1)
        
    def get_eid(self):
        """
        Returns event ids
        """
        return(self._datadict['eid'])
    

class mts(Inputdata):
    """
    Base class for multivarite timeseries data objects consumed by causal algorithms
    """

    def __init__(self):
        """
        Initialize an empty dictionary that will hold
        all the data
        """
        super(mts, self).__init__()
                
