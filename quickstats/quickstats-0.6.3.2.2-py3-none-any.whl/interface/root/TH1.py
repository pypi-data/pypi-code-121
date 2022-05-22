import uuid
import array
import numpy as np

import ROOT

from quickstats.interface.root import TObject, TArrayData
from quickstats.interface.root import load_macro
from quickstats.interface.cppyy.vectorize import as_vector, as_np_array, as_c_array, np_type_str_maps

class TH1(TObject):
    
    FUNDAMENTAL_TYPE = ROOT.TH1
    
    def __init__(self, h:ROOT.TH1, dtype:str='double', 
                 underflow_bin:int=0,
                 overflow_bin:int=0):
        self.dtype = dtype
        self.underflow_bin = underflow_bin
        self.overflow_bin  = overflow_bin
        self.init(h)
        
    def init(self, h):
        self.bin_content  = self.GetBinContentArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_error    = self.GetBinErrorArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_center   = self.GetBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_width    = self.GetBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_low_edge = self.GetBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        
    @staticmethod
    def _to_ROOT(name:str, bin_content, bin_width=None, bin_center=None, bin_low_edge=None,
                 bin_error=None, title:str=None):
        if ((bin_low_edge is None) and (bin_center is None)) or \
           ((bin_low_edge is not None) and (bin_center is not None)):
            raise ValueError("must provide either bin low edge or bin center values")
        n_bins = len(bin_content)
        if bin_center is not None:
            if bin_width is None:
                if n_bins < 2:
                    raise ValueError("unable to determine bin width with only one bin")
                bin_width = (bin_center[1] - bin_center[0])
            bin_low_edge = bin_center - bin_width/2
        if len(bin_low_edge) == n_bins:
            bin_width = (bin_low_edge[-1] - bin_low_edge[-2])
            bin_low_edge = np.insert(bin_low_edge, len(bin_low_edge), bin_low_edge[-1] + bin_width)
        if title is None:
            title = name
        dtype = bin_content.dtype
        if np_type_str_maps[dtype] == "float":
            h_func = ROOT.TH1F
        else:
            h_func = ROOT.TH1D
        h = h_func(name, title, n_bins, as_c_array(bin_low_edge))
        if bin_error is None:
            bin_error = np.zeros((n_bins,))
        for i in range(n_bins):
            h.SetBinContent(i + 1, bin_content[i])
            h.SetBinError(i + 1, bin_error[i])
        return h
    
    def to_ROOT(self, name:str, title:str=None):
        if title is None:
            title = name
        return self._to_ROOT(name, self.bin_content, bin_low_edge=self.bin_low_edge,
                             bin_error=self.bin_error, title=title)
        
    @staticmethod
    def GetBinContentArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinContentArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)        
        
    @staticmethod
    def GetBinErrorArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinErrorArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
                     
    @staticmethod
    def GetBinErrorUpArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinErrorUpArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinErrorLowArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinErrorLowArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)                     

    @staticmethod
    def GetBinCenterArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinCenterArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetBinWidthArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinWidthArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinLowEdgeArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinLowEdgeArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetPoissonError(data:np.ndarray):
        c_data = as_vector(data)
        c_result  = ROOT.THistUtils.GetPoissonError(c_data)
        result = as_np_array(c_result)
        data_size = data.shape[0]
        pois_error = {
            'lo': result[:data_size],
            'hi': result[data_size:]
        }
        return pois_error
        