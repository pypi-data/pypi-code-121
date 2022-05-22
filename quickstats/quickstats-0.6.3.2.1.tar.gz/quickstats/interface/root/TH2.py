import array
import numpy as np

import ROOT

from quickstats.interface.root import TObject, TArrayData
from quickstats.interface.cppyy.vectorize import c_array_to_np_array

class TH2(TObject):
    
    FUNDAMENTAL_TYPE = ROOT.TH2
    
    DTYPE_MAP = {
        ROOT.TH2I: "int",
        ROOT.TH2F: "float",
        ROOT.TH2D: "double"
    }
    
    def __init__(self, h:ROOT.TH2, underflow_bin:bool=False, overflow_bin:bool=False):
        self.dtype = self.DTYPE_MAP.get(type(h), "double")
        self.underflow_bin = underflow_bin
        self.overflow_bin  = overflow_bin
        self.init(h)
        
    def init(self, h):
        self.bin_content    = self.GetBinContentArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_labels       = self.GetXLabelArray(h)
        self.y_labels       = self.GetYLabelArray(h)
        self.x_bin_center   = self.GetXBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_center   = self.GetYBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_bin_width    = self.GetXBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_width    = self.GetYBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_bin_low_edge = self.GetXBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_low_edge = self.GetYBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin) 
        
    @staticmethod
    def GetBinContentArray(h, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        arr = h.GetArray()
        n_bins_x = h.GetNbinsX()
        n_bins_y = h.GetNbinsY()
        # account for underflow and overflow bins
        size = (n_bins_x + 2) * (n_bins_y + 2)
        np_arr = c_array_to_np_array(arr, size=size, shape=(n_bins_x + 2, n_bins_y + 2))
        x_start = 1 if not underflow_bin else 0
        y_start = x_start
        x_end = -1 if not overflow_bin else n_bins_x + 2
        y_end = -1 if not overflow_bin else n_bins_y + 2
        np_arr = np_arr[x_start:x_end, y_start:y_end]
        return np_arr
    
    @staticmethod
    def GetXLabelArray(h:ROOT.TH2):
        return np.array(h.GetXaxis().GetLabels(), dtype=str)
    
    @staticmethod
    def GetYLabelArray(h:ROOT.TH2):
        return np.array(h.GetYaxis().GetLabels(), dtype=str)
    
    @staticmethod
    def GetAxisBinCenterArray(ax:ROOT.TAxis, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TAxisUtils.GetBinCenterArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetAxisBinWidthArray(ax:ROOT.TAxis, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TAxisUtils.GetBinWidthArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetAxisBinLowEdgeArray(ax:ROOT.TAxis, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TAxisUtils.GetBinLowEdgeArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetXBinCenterArray(h:ROOT.TH2, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH2.GetAxisBinCenterArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinCenterArray(h:ROOT.TH2, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH2.GetAxisBinCenterArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetXBinWidthArray(h:ROOT.TH2, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH2.GetAxisBinWidthArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinWidthArray(h:ROOT.TH2, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH2.GetAxisBinWidthArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)

    @staticmethod
    def GetXBinLowEdgeArray(h:ROOT.TH2, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        return TH2.GetAxisBinLowEdgeArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinLowEdgeArray(h:ROOT.TH2, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        return TH2.GetAxisBinLowEdgeArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def correlationHist_to_dataframe(h:ROOT.TH2):
        dtype = TH2.DTYPE_MAP.get(type(h), "double")
        data = TH2.GetBinContentArray(h, dtype)
        xlabels = TH2.GetXLabelArray(h)
        ylabels = TH2.GetYLabelArray(h)
        if not np.array_equal(xlabels, ylabels):
            raise RuntimeError("invalid correlation histogram: labels along x-axis and y-axis do not match")
        if (data.shape[0] != len(xlabels)) or (data.shape[1] != len(ylabels)):
            raise RuntimeError("invaiid correlation histogram: size of matrix does not match number of labels")
        _data = {}
        for i, label in enumerate(xlabels):
            _data[label] = data[:, i]
        import pandas as pd
        df = pd.DataFrame(_data)
        df.index = ylabels[::-1]
        return df