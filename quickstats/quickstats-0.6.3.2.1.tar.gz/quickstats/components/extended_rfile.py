##################################################################################################
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
import os
import sys
from typing import List, Optional, Union, Dict, Set

import numpy as np

import ROOT

import quickstats
from quickstats import semistaticmethod
from quickstats.components import AbstractObject
from quickstats.interface.root import TH1

class ExtendedRFile(AbstractObject):
    
    def __init__(self, fname:str, tree_name:Optional[str]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.fname = fname
        self.tree_name = tree_name
        self.initialize()
        
    @property
    def file(self):
        return self._file
    
    @property
    def components(self):
        return self._components
    
    @property
    def rdf(self):
        return self._rdf
    
    @property
    def rdf_map(self):
        return self._rdf_map
    
    @property
    def cache(self):
        return self._cache
    
    @property
    def canvas(self):
        return self._canvas
    
    @staticmethod
    def is_corrupt(f:ROOT.TFile):
        if f.IsZombie():
            return True
        if f.TestBit(ROOT.TFile.kRecovered):
            return True
        if f.GetNkeys() == 0:
            return True
        return False
        
    def initialize(self):
        if not os.path.exists(self.fname):
            raise FileNotFoundError('workspace file {} does not exist'.format(self.fname))
        self.stdout.info('INFO: Opening file "{}"'.format(self.fname))
        file = ROOT.TFile(self.fname) 
        if self.is_corrupt(file):
            raise RuntimeError("root file is corrupted")
        self._file = file
        
        self._rdf_map = {}
        self._rdf     = None
        if self.tree_name is not None:
            self.set_tree(self.tree_name)
            
        self._canvas = None
        self._cache  = []
        self._components = []
        
    def canvas_draw(self):
        if not self.canvas:
            self._canvas = ROOT.TCanvas()
        self.canvas.Draw()
    
    def add_tree(self, tree_name:str):
        if tree_name in self._rdf_map:
            self.stdout.info("INFO: Tree already added to the rdf collection.")
            return None
        rdf = ROOT.RDataFrame(tree_name, self.fname)
        if not rdf:
            raise RuntimeError(f"failed to load tree \"{self.tree_name}\"")
        self._rdf_map[tree_name] = rdf
        self.stdout.info(f"INFO: Added tree \"{tree_name}\" to the rdf collection")
        
    def set_tree(self, tree_name:str):
        if tree_name not in self._rdf_map:
            self.add_tree(tree_name)
        self._rdf = self._rdf_map[tree_name]
        self.stdout.info(f"INFO: Set active tree to \"{tree_name}\"")
    
    def validate(self):
        if self._rdf is None:
            raise RuntimeError("active tree not set")
            
    def get_Histo1D(self, name:str, n_bin:int, xmin:float, xmax:float, column:str, weight:Optional[str]=None,
                    title:Optional[str]=None, pyobject:bool=False, draw:bool=False, draw_option:Optional[str]=None):
        self.validate()
        if title is None:
            title = name
        if weight is None:
            r_th1_ptr = self.rdf.Histo1D((name, title, n_bin, xmin, xmax), column)
        else:
            r_th1_ptr = self.rdf.Histo1D((name, title, n_bin, xmin, xmax), column, weight)
        r_th1 = r_th1_ptr.GetPtr()
        if draw:
            if draw_option is None:
                draw_option = ""
            r_th1.Draw(draw_option)
            self.add_cache(r_th1)
            self.canvas_draw()
        if pyobject:
            py_th1 = TH1(r_th1)
            return py_th1
        return r_th1
    
    def append(self, robject:ROOT.TObject):
        if not isinstance(robject, ROOT.TObject):
            raise RuntimeError("only TObject can be added to TFile")
        self.stdout.info(f"INFO: Added object \"{robject.GetName()}\" to internal components")
        self._components.append(robject)
    
    def add_cache(self, robject:ROOT.TObject):
        self.stdout.info(f"INFO: Added object \"{robject.GetName()}\" to cache")
        self._cache.append(robject)
        
    def clear_cache(self):
        self._cache = []
    
    def save_components(self, fname:str, mode:str="RECREATE", components:Optional[List]=None):
        if components is None:
            components = self.components
        f = ROOT.TFile(fname, mode)
        f.cd()
        for component in components:
            component.Write()
        f.Close()