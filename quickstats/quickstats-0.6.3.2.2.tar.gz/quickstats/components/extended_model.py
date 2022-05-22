##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
import os
import sys
import copy
import math
import fnmatch
from typing import List, Optional, Union, Dict, Set, Tuple

import numpy as np

import ROOT

import quickstats
from quickstats import semistaticmethod
from quickstats.components import AbstractObject
from quickstats.maths.numerics import is_integer, pretty_value, get_bins_given_edges, array_issubset
from quickstats.utils.root_utils import load_macro
from quickstats.utils.common_utils import str_list_filter
from quickstats.utils.roofit_utils import (get_variable_attributes, variable_collection_to_dataframe,
                                           get_relevant_components)
from quickstats.interface.root import TH1, RooDataSet, RooArgSet, RooMsgService
from quickstats.interface.root import roofit_extension as rf_ext
from quickstats.components.basics import WSVariables, SetValueMode

class ExtendedModel(AbstractObject):
    
    _DEFAULT_CONSTR_CLS_ = ["RooGaussian", "RooLognormal", "RooGamma", "RooPoisson", "RooBifurGauss"]
    
    _DEFAULT_NAMES_ = {
        'conditional_globs': 'conditionalGlobs_{mu}',
        'conditional_nuis': 'conditionalNuis_{mu}',
        'nominal_globs': 'nominalGlobs',
        'nominal_nuis': 'nominalNuis',
        'nominal_vars': 'nominalVars',
        'weight': 'weightVar',
        'dataset_args': 'obsAndWeight',
        'asimov': 'asimovData_{mu}',
        'asimov_no_poi': 'asimovData',
        'channel_asimov': 'combAsimovData_{label}',
        'nll_snapshot': '{nll_name}_{mu}',
        'range_sideband_low': 'SBLo',
        'range_blind': 'Blind',
        'range_sideband_high': 'SBHi'
    }
    
    def __init__(self, fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None,
                 data_name:Optional[str]="combData", snapshot_name:Optional[Union[List[str], str]]=None,
                 binned_likelihood:bool=True, tag_as_measurement:Optional[str]=None,
                 fix_cache:bool=True, fix_multi:bool=True, interpolation_code:int=-1,
                 load_extension:bool=True, verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.fname = fname
        self.ws_name = ws_name
        self.mc_name = mc_name
        self.data_name = data_name
        self.initial_snapshots = snapshot_name
        self.binned_likelihood = binned_likelihood
        self.tag_as_measurement = tag_as_measurement
        self.fix_cache = fix_cache
        self.fix_multi = fix_multi
        self.interpolation_code = interpolation_code
        
        quickstats.load_corelib()
        if load_extension:
            self.load_extension()
        
        self.initialize()
  
    @property
    def file(self):
        return self._file
    @property
    def workspace(self):
        return self._workspace
    @property
    def model_config(self):
        return self._model_config
    @property
    def pdf(self):
        return self._pdf
    @property
    def data(self):
        return self._data
    @property
    def nuisance_parameters(self):
        return self._nuisance_parameters
    @property
    def global_observables(self):
        return self._global_observables
    @property
    def pois(self):
        return self._pois
    @property
    def observables(self):
        return self._observables
    
    @property
    def category(self):
        return self._category
    
    @property
    def data_cat(self):
        return self._data_cat
    
    @property
    def initial_snapshots(self):
        return self._initial_snapshots
    
    @initial_snapshots.setter
    def initial_snapshots(self, val):
        if val is None:
            self._initial_snapshots = []
        elif isinstance(val, str):
            self._initial_snapshots = [s.strip() for s in val.split(',') if s]
        elif isinstance(val, list):
            self._initial_snapshots = val
        else:
            raise ValueError("\"initial_snapshots\" must be string or list of strings")
    
    @semistaticmethod
    def load_extension(self):
        extensions = quickstats.get_workspace_extensions()
        for extension in extensions:
            result = load_macro(extension)
            if (result is not None) and hasattr(ROOT, extension):
                self.stdout.info(f'INFO: Loaded extension module "{extension}"')
        
    @semistaticmethod
    def modify_interp_codes(self, ws, interp_code, classes=None):
        if classes is None:
            classes = [ROOT.RooStats.HistFactory.FlexibleInterpVar, ROOT.PiecewiseInterpolation]
        for component in ws.components():
            for cls in classes:
                if (component.IsA() == cls.Class()):
                    component.setAllInterpCodes(interp_code)
                    class_name = cls.Class_Name().split('::')[-1]
                    self.stdout.info('INFO: {} {} interpolation code set to {}'.format(component.GetName(),
                                                                            class_name,
                                                                            interp_code))
        return None           

    @semistaticmethod
    def activate_binned_likelihood(self, ws):
        for component in ws.components():
            try:
                flag = (component.IsA() == ROOT.RooRealSumPdf.Class())
            except:
                flag = (component.ClassName() == "RooRealSumPdf")
            if (flag):
                component.setAttribute('BinnedLikelihood')
                self.stdout.info('INFO: Activated binned likelihood attribute for {}'.format(component.GetName()))
        return None
                          
    @semistaticmethod
    def set_measurement(self, ws, condition):
        for component in ws.components():
            name = component.GetName()
            try:
                flag = (component.IsA() == ROOT.RooAddPdf.Class())
            except:
                flag = (component.ClassName() == "RooAddPdf")
            if flag and condition(name):
                component.setAttribute('MAIN_MEASUREMENT')
                self.stdout.info('INFO: Activated main measurement attribute for {}'.format(name))
        return None
    
    @semistaticmethod
    def deactivate_lv2_const_optimization(self, ws, condition):
        self.stdout.info('INFO: Deactivating level 2 constant term optimization for specified pdfs')
        for component in ws.components():
            name = component.GetName()
            if (component.InheritsFrom(ROOT.RooAbsPdf.Class()) and condition(name)):
                component.setAttribute("NOCacheAndTrack")
                self.stdout.info('INFO: Deactivated level 2 constant term optimization for {}'.format(name))
                
    def load_snapshots(self, snapshot_names:List[str]):
        for snapshot_name in snapshot_names:
            if self.workspace.getSnapshot(snapshot_name):
                self.workspace.loadSnapshot(snapshot_name)
                self.stdout.info(f'INFO: Loaded snapshot "{snapshot_name}"')
            else:
                self.stdout.warning(f'WARNING: Failed to load snapshot "{snapshot_name}"')
            
    def initialize(self):
        if isinstance(self.fname, str):
            if not os.path.exists(self.fname):
                raise FileNotFoundError(f'workspace file "{self.fname}" does not exist')
            self.stdout.info(f'INFO: Opening file "{self.fname}"')
            file = ROOT.TFile(self.fname) 
            if (not file):
                raise RuntimeError(f"Something went wrong while loading the root file: {self.fname}")
            # load workspace
            if self.ws_name is None:
                ws_names = [i.GetName() for i in file.GetListOfKeys() if i.GetClassName() == 'RooWorkspace']
                if not ws_names:
                    raise RuntimeError(f"No workspaces found in the root file: {self.fname}")
                if len(ws_names) > 1:
                    self.stdout.warning("WARNING: Found multiple workspace instances from the root file: "
                                        f"{self.fname}. Available workspaces are \"{','.join(ws_names)}\". "
                                        f"Will choose the first one by default")
                self.ws_name = ws_names[0]
            ws = file.Get(self.ws_name)
        elif isinstance(self.fname, ROOT.RooWorkspace):
            file = None
            ws = self.fname
        if not ws:
            raise RuntimeError(f'failed to load workspace "{self.ws_name}"')
        self.ws_name = ws.GetName()
        self.stdout.info(f'INFO: Loaded workspace "{self.ws_name}"')
        # load model config
        if self.mc_name is None:
            mc_names = [i.GetName() for i in ws.allGenericObjects() if 'ModelConfig' in i.ClassName()]
            if not mc_names:
                raise RuntimeError(f"no ModelConfig object found in the workspace: {ws_name}")
            if len(mc_names) > 1:
                self.stdout.warning(f"WARNING: Found multiple ModelConfig instances from the workspace: {ws_name}. "
                                    f"Available ModelConfigs are \"{','.join(mc_names)}\". "
                                    "Will choose the first one by default")
            self.mc_name = mc_names[0]
        model_config = ws.obj(self.mc_name)
        if not model_config:
            raise RuntimeError(f'failed to load model config "{self.mc_name}"')
        self.stdout.info(f'INFO: Loaded model config "{self.mc_name}"')
            
        # modify interpolation code
        if self.interpolation_code != -1:
            self.modify_interp_codes(ws, self.interpolation_code,
                                     classes=[ROOT.RooStats.HistFactory.FlexibleInterpVar, ROOT.PiecewiseInterpolation])
        
        # activate binned likelihood
        if self.binned_likelihood:
            self.activate_binned_likelihood(ws)
        
        # set main measurement
        if self.tag_as_measurement:
            self.set_measurement(ws, condition=lambda name: name.startswith(self.tag_as_measurement))
                          
        # deactivate level 2 constant term optimization
            self.deactivate_lv2_const_optimization(ws, 
                condition=lambda name: (name.endswith('_mm') and 'mumu_atlas' in name))

        # load pdf
        pdf = model_config.GetPdf()
        if not pdf:
            raise RuntimeError('Failed to load pdf')
        self.stdout.info(f'INFO: Loaded model pdf "{pdf.GetName()}" from model config')
             
        # load dataset
        if self.data_name is None:
            data_names = [i.GetName() for i in ws.allData()]
            if not data_names:
                raise RuntimeError(f"no datasets found in the workspace: {ws_name}")
            self.data_name = data_names[0]
        data = ws.data(self.data_name)
        if not data:
            raise RuntimeError(f'failed to load dataset \"{self.data_name}\"')
        self.stdout.info('INFO: Loaded dataset "{}" from workspace'.format(data.GetName()))
                
        # load nuisance parameters
        nuisance_parameters = model_config.GetNuisanceParameters()
        if not nuisance_parameters:
            #raise RuntimeError('Failed to load nuisance parameters')
            self.stdout.warning("WARNING: No nuisance parameters found in the workspace. "
                                "An empty set will be loaded by default.")
            nuisance_parameters = ROOT.RooArgSet()
            model_config.SetNuisanceParameters(nuisance_parameters)
        else:
            self.stdout.info('INFO: Loaded nuisance parameters from model config')
                
        # Load global observables
        global_observables = model_config.GetGlobalObservables()
        if not global_observables:
            self.stdout.warning("WARNING: No global observables found in the workspace. "
                                "An empty set will be loaded by default.")            
            global_observables = ROOT.RooArgSet()
        else:
            self.stdout.info('INFO: Loaded global observables from model config')                  
    
        # Load POIs
        pois = model_config.GetParametersOfInterest()
        if not pois:
            raise RuntimeError('Failed to load parameters of interest')
        self.stdout.info('INFO: Loaded parameters of interest from model config')
                                  
        # Load observables
        observables = model_config.GetObservables()
        if not observables:
            raise RuntimeError('Failed to load observables')     
        self.stdout.info('INFO: Loaded observables from model config')
        
        # get categories in case pdf is RooSimultaneous
        if pdf.ClassName() == "RooSimultaneous":
            category = pdf.indexCat()
        else:
            category = None
        
        # split dataset according to categories
        if category is not None:
            data_cat = data.split(category, True)
        else:
            data_cat = None
        
        self._file                = file
        self._workspace           = ws
        self._model_config        = model_config
        self._pdf                 = pdf
        self._data                = data
        self._nuisance_parameters = nuisance_parameters
        self._global_observables  = global_observables
        self._pois                = pois
        self._observables         = observables
        self._category            = category
        self._data_cat            = data_cat
                          
        # Load snapshots
        self.load_snapshots(self.initial_snapshots)
        
        RooMsgService.remove_topics()
        return None
                
    def set_parameters_with_expression(self, param_expr:Optional[str]=None,
                                       source:Optional["ROOT.RooArgSet"]=None,
                                       mode:Union[str, SetValueMode]=SetValueMode.UNCHANGED):
        if source is None:
            source = self.workspace.allVars()
        param_dict = self.parse_param_expr(param_expr)
        parameters = self._set_parameters(source, param_dict, mode=mode)
        if not parameters:
            self.stdout.warning("WARNING: No parameters are modified from the given fix / profile expression", "red")
        return parameters
        
    def fix_parameters(self, param_expr:Optional[str]=None, source:Optional["ROOT.RooArgSet"]=None):
        return self.set_parameters_with_expression(param_expr, source, mode=SetValueMode.FIX)
    
    def profile_parameters(self, param_expr:Optional[str]=None, source:Optional["ROOT.RooArgSet"]=None):
        return self.set_parameters_with_expression(param_expr, source, mode=SetValueMode.FREE)
    
    def _set_parameters(self, source:"ROOT.RooArgSet", param_dict:Dict, 
                        mode:Union[str, SetValueMode]=SetValueMode.UNCHANGED):
        selected_parameters = []
        source_names = [param.GetName() for param in source]
        for name in param_dict:
            # resolve variable set
            if name.startswith("<") and name.endswith(">"):
                selected_params = self.get_variables(name.strip("<>"))
            else:
                selected_params = [sname for sname in source_names if fnmatch.fnmatch(sname, name)]
            if not selected_params:
                self.stdout.warning(f'WARNING: Parameter "{name}" does not exist. No modification will be made.', "red")
            for param in selected_params:
                if isinstance(param, str):
                    param = source[param]
                self._set_parameter(param, param_dict[name], mode=mode)
                selected_parameters.append(param)
        return selected_parameters

    def _set_parameter(self, param:"ROOT.RooRealVar", value:Union[float, int, List, Tuple], 
                       mode:Union[str, SetValueMode]=SetValueMode.UNCHANGED):
        mode = SetValueMode.parse(mode)
        name = param.GetName()
        old_value = param.getVal()
        new_value = old_value
        if isinstance(value, (float, int)):
            new_value = value
        elif isinstance(value, (list, tuple)):
            if len(value) == 3:
                new_value = value[0]
                v_min, v_max = value[1], value[2]
            elif len(value) == 2:
                v_min, v_max = value[0], value[1]
            else:
                raise ValueError('invalid expression for profiling parameter: {}'.format(value))
            if new_value is None:
                new_value = old_value
            # set range
            if (v_min is not None) and (v_max is not None):
                if (new_value < v_min) or (new_value > v_max):
                    new_value = (v_min + v_max)/2
                param.setRange(v_min, v_max)
            elif (v_min is not None):
                if (new_value < v_min):
                    new_value = v_min
                # lower bound is zero, if original value is negative, will flip to positive value
                if (v_min == 0) and (old_value < 0):
                    new_value = abs(old_value)
                param.setMin(v_min)
            elif (v_max is not None):
                if (new_value > v_max):
                    new_value = v_max
                if (v_max == 0) and (old_value > 0):
                    new_value = -abs(old_value)
                param.setMax(v_max)
        if new_value != old_value:
            param.setVal(new_value)
        if mode == SetValueMode.FIX:
            param.setConstant(1)
            self.stdout.info(f"INFO: Fixed parameter \"{name}\" at value {param.getVal()} "
                             f"[{param.getMin()}, {param.getMax()}]")
        elif mode == SetValueMode.FREE:
            param.setConstant(0)
            self.stdout.info(f"INFO: Float parameter \"{name}\" at value {param.getVal()} "
                             f"[{param.getMin()}, {param.getMax()}]")
        else:
            state_str = "C" if param.isConstant() else "F"
            self.stdout.info(f"INFO: Set parameter \"{name}\" at value {param.getVal()} "
                             f"[{param.getMin()}, {param.getMax()}] {state_str}")

    def set_parameter_defaults(self, source:"ROOT.RooArgSet", value:float=None, error:float=None,
                               constant:bool=None, remove_range:bool=None, target:List[str]=None):
        for param in source:
            if (not target) or (param.GetName() in target):
                if remove_range:
                    param.removeRange()            
                if value is not None:
                    param.setVal(value)
                if error is not None:
                    param.setError(error)
                if constant is not None:
                    param.setConstant(constant)
    
    @staticmethod
    def parse_param_expr(param_expr:str=None):
        param_dict = {}
        # if parameter expression is not empty string or None
        if param_expr: 
            if isinstance(param_expr, str):
                param_dict = ExtendedModel.parse_param_str(param_expr)
            elif isinstance(param_expr, dict):
                param_dict = param_dict
            else:
                raise ValueError('invalid format for parameter expression: {}'.format(param_expr))
        elif param_expr is None:
        # if param_expr is None, all parameters will be parsed as None by default
            param_dict = {param.GetName():None for param in source}
        return param_dict

    @staticmethod
    def parse_param_str(param_str):
        '''
        Example: "param_1,param_2=0.5,param_3=-1,param_4=1,param_5=_0_100,param_6=__100,param_7=_0_"
        '''
        param_str = param_str.replace(' ', '')
        param_list = param_str.split(',')
        param_dict = {}
        for param_expr in param_list:
            expr = param_expr.split('=')
            # case only parameter name is given
            if len(expr) == 1:
                param_dict[expr[0]] = None
            # case both parameter name and value is given
            elif len(expr) == 2:
                param_name = expr[0]
                param_values = [float(v) if v else None for v in expr[1].split("_")]
                if len(param_values) == 1:
                    param_values = param_values[0]
                param_dict[param_name] = param_values
            else:
                raise ValueError('invalid parameter expression: {}'.format(param))
        return param_dict
    
    @staticmethod
    def randomize_globs(pdf:ROOT.RooAbsPdf, globs:ROOT.RooDataSet, seed:int):
        """Randomize values of global observables (for generating pseudo-experiments)
        """
        # set random seed for reproducible result
        if seed >= 0:
            ROOT.RooRandom.randomGenerator().SetSeed(seed)
        pseudo_globs = pdf.generateSimGlobal(globs, 1)
        pdf_vars = pdf.getVariables()
        pdf_vars.assignValueOnly(pseudo_globs.get(0))

    def unfold_constraints(self, constr_cls:Optional[List[str]]=None,
                           recursion_limit:int=50, strip_disconnected:bool=False):
        constraints = self.get_all_constraints()
        unfolded_constraints = rf_ext.unfold_constraints(constraints, self.observables, self.nuisance_parameters,
                                                         constraint_cls=constr_cls,
                                                         recursion_limit=recursion_limit,
                                                         strip_disconnected=strip_disconnected)
        return unfolded_constraints
    
    def pair_constraints(self, fmt:str="list", to_str=False, sort:bool=True, base_component:bool=False):
        constraint_pdfs = self.unfold_constraints()
        if base_component:
            # for glob value matching
            return rf_ext.pair_constraints_base_component(constraint_pdfs, self.nuisance_parameters,
                                                          self.global_observables, fmt=fmt,
                                                          sort=sort, to_str=to_str)
        return rf_ext.pair_constraints(constraint_pdfs, self.nuisance_parameters,
                                       self.global_observables, fmt=fmt,
                                       sort=sort, to_str=to_str)
    
    def get_constrained_nuisance_parameters(self):
        """Get the list of constrained nuisance parameters instances
        """
        _, constrained_nuis, _ = self.pair_constraints()
        return constrained_nuis
    
    def get_unconstrained_nuisance_parameters(self, constrained_nuis=None):
        """Get the list of unconstrained nuisance parameters instances
        """
        # do not re-isolate constrained nuisance parameters
        if constrained_nuis is None:
            constrained_nuis = self.get_constrained_nuisance_parameters()
        unconstrained_nuis = list(set(self.nuisance_parameters) - set(constrained_nuis))
        return unconstrained_nuis
    
    def set_constrained_nuisance_parameters_to_nominal(self, set_constant:bool=False):
        constrain_pdf, constrained_nuis, _ = self.pair_constraints(fmt="arglist", sort=False)
        for pdf, nuis in zip(constrain_pdf, constrained_nuis):
            pdf_class = pdf.ClassName()
            if pdf_class in ["RooGaussian", "RooBifurGauss"]:
                nuis.setVal(0)
            elif pdf_class == "RooPoisson":
                nuis.setVal(1)
            else:
                raise RuntimeError(f"constraint term \"{pdf.GetName()}\" has unsupported type \"{pdf_class}\"")
        if set_constant:
            for nuis in constrained_nuis:
                nuis.setConstant(1)
    
    def get_all_constraints(self, pdf:Optional[ROOT.RooAbsPdf]=None, cache:bool=True):
        if pdf is None:
            pdf = self.pdf
        all_constraints = ROOT.RooArgSet()
        cache_name = "CACHE_CONSTR_OF_PDF_{}_FOR_OBS_{}".format(self.pdf.GetName(), 
                     ROOT.RooNameSet(self.data.get()).content())                 
        constr_cache = self.workspace.set(cache_name)
        if constr_cache and cache:
            # retrieve constrains from cache     
            all_constraints.add(constr_cache)
        else:
            # load information needed to determine attributes from ModelConfig 
            obs = self.observables.Clone()
            nuis = self.nuisance_parameters.Clone()
            all_constraints = pdf.getAllConstraints(obs, nuis, ROOT.kFALSE)
            if (not constr_cache) and cache:
                self.workspace.defineSet(cache_name, all_constraints)
        """
        # update: there is no need to
        # take care of the case where we have a product of constraint terms
        temp_all_constraints = ROOT.RooArgSet(all_constraints.GetName())
        for constraint in all_constraints:
            if constraint.IsA() == ROOT.RooProdPdf.Class():
                buffer = ROOT.RooArgSet()
                ROOT.RooFitExt.unfoldProdPdfComponents(constraint, buffer)
                temp_all_constraints.add(buffer)
            else:
                temp_all_constraints.add(constraint)
        return temp_all_constraints
        """
        return all_constraints
    
    def inspect_constrained_nuisance_parameter(self, nuis, constraints):
        nuis_name = nuis.GetName()
        self.stdout.info('INFO: On nuisance parameter {}'.format(nuis_name))
        nuip_nom = 0.0
        prefit_variation = 1.0
        found_constraint = ROOT.kFALSE
        found_gaussian_constraint = ROOT.kFALSE
        constraint_type = None
        for constraint in constraints:
            constr_name = constraint.GetName()
            if constraint.dependsOn(nuis):
                found_constraint = ROOT.kTRUE
                constraint_type = 'unknown'
                # Loop over global observables to match nuisance parameter and
                # global observable in case of a constrained nuisance parameter
                found_global_observable = ROOT.kFALSE
                for glob_obs in self.global_observables:
                    if constraint.dependsOn(glob_obs):
                        found_global_observable = ROOT.kTRUE
                        # find constraint width in case of a Gaussian
                        if constraint.IsA() == ROOT.RooGaussian.Class():
                            found_gaussian_constraint = ROOT.kTRUE
                            constraint_type = 'gaus'
                            old_sigma_value = 1.0
                            found_sigma = ROOT.kFALSE
                            for server in constraint.servers():
                                if (server != glob_obs) and (server != nuis):
                                    old_sigma_value = server.getVal()
                                    found_sigma = ROOT.kTRUE
                            if math.isclose(old_sigma_value, 1.0, abs_tol=0.001):
                                old_sigma_value = 1.0
                            if not found_sigma:
                                self.stdout.info(f'INFO: Sigma for pdf {constr_name} not found. Uisng 1.0.')
                            else:
                                self.stdout.info('INFO: Uisng {} for sigma of pdf {}'.format(old_sigma_value, constr_name))

                            prefit_variation = old_sigma_value
                        elif constraint.IsA() == ROOT.RooPoisson.Class():
                            constraint_type = 'pois'
                            tau = glob_obs.getVal()
                            self.stdout.info(f'INFO: Found tau {constr_name} of pdf')
                            prefit_variation = 1. / math.sqrt(tau)
                            self.stdout.info(f'INFO: Prefit variation is {prefit_variation}')
                            nuip_nom = 1.0
                            self.stdout.info(f"INFO: Assume that {nuip_nom} is nominal value of the nuisance parameter")
        return prefit_variation, constraint_type, nuip_nom
    
    def create_blind_range(self, blind_range:List[float], categories:Optional[List[str]]=None):
        """Create blind ranges for observables
        
        Arguments
            blind_range: list of float
                A list of the form [<lower_blind_range>, <upper_blind_range>]
            categories: (Optional) list of string
                List of categories from which the observables will have their blind range created.
                All categories are used by default.
        """
        if len(blind_range) != 2:
            raise ValueError("invalid format for blind range, must be list of the form [xmin, xmax]")
        range_name_SBLo  = self._DEFAULT_NAMES_['range_sideband_low']
        range_name_Blind = self._DEFAULT_NAMES_['range_blind']
        range_name_SBHi  = self._DEFAULT_NAMES_['range_sideband_high']
        padding = max([len(range_name_SBLo), len(range_name_Blind), len(range_name_SBHi)]) + 2
        blind_min = blind_range[0]
        blind_max = blind_range[1]
        category_map = self.get_category_map()
        if categories is None:
            categories = list(category_map)
        for category in categories:
            obs_name = category_map[category]['observable']
            obs = self.workspace.var(obs_name)
            obs_range = obs.getRange()
            obs_min = obs_range.first
            obs_max = obs_range.second
            if (blind_max <= blind_min) or (blind_max > obs_max) or (blind_min < obs_min):
                raise ValueError(f"invalid blinding range provided: min={blind_min}, max={blind_max}")
            _range_name_SBLo  = f"{range_name_SBLo}_{category}"
            _range_name_Blind = f"{_range_name_Blind}_{category}"
            _range_name_SBHi  = f"{_range_name_SBHi}_{category}"            
            obs.setRange(_range_name_SBLo, obs_min, blind_min)
            obs.setRange(_range_name_Blind, blind_min, blind_max)
            obs.setRange(_range_name_SBHi, blind_max, obs_max)
            cat_padding = padding + len(category)
            self.stdout.info(f"INFO: The following ranges are defined for the observable \"{obs_name}\"")
            self.stdout.info(f"\t{_range_name_SBLo.ljust(cat_padding)}: [{obs_min}, {blind_min}]")
            self.stdout.info(f"\t{_range_name_Blind.ljust(cat_padding)}: [{blind_min}, {blind_max}]")
            self.stdout.info(f"\t{_range_name_SBHi.ljust(cat_padding)}: [{blind_max}, {obs_max}]")
        return None
    
    def get_sideband_range_name(self):
        """Get sideband range name to be used in RooAbsPdf.createNLL(..., Range(<range_name>))
        """
        range_name_SBLo = self._DEFAULT_NAMES_['range_sideband_low']
        range_name_SBHi = self._DEFAULT_NAMES_['range_sideband_high']
        return f"{range_name_SBLo},{range_name_SBHi}"
    
    def get_blind_range_name(self):
        """Get blind range name that are excluded from the fit range of the observable
        """
        return self._DEFAULT_NAMES_['range_blind']
    
    def get_blind_range(self):
        category_map = self.get_category_map()
        blind_range_name = self.get_blind_range_name()
        blind_range = {}
        for category in category_map:
            obs_name = category_map[category]['observable']
            obs = self.workspace.var(obs_name)
            dummy_range = obs.getRange(blind_range_name)
            dummy_min = dummy_range.first
            dummy_max = dummy_range.second
            obs_range = obs.getRange()
            obs_min = obs_range.first
            obs_max = obs_range.second
            if (dummy_min == obs_min) and (dummy_max == obs_max):
                # observable not blinded, skipping
                continue
            blind_range[obs_name] = [dummy_min, dummy_max]
        return blind_range
    
    def remove_blind_range(self, categories:Optional[List[str]]=None):
        category_map = self.get_category_map()
        if categories is None:
            categories = list(category_map)
        range_name_SBLo = self._DEFAULT_NAMES_['range_sideband_low']
        range_name_Blind = self._DEFAULT_NAMES_['range_blind']
        range_name_SBHi = self._DEFAULT_NAMES_['range_sideband_high']
        blind_range = self.get_blind_range()
        for category in categories:
            obs_name = category_map[category]['observable']
            if obs_name not in blind_range:
                continue
            obs = self.workspace.var(obs_name)
            obs_range = obs.getRange()
            obs_min = obs_range.first
            obs_max = obs_range.second            
            obs.setRange(range_name_SBLo, obs_min, obs_max)
            obs.setRange(range_name_Blind, obs_min, obs_max)
            obs.setRange(range_name_SBHi, obs_min, obs_max)
            self.stdout.info(f"INFO: The following ranges are removed from the observable \"{obs_name}\":")
            self.stdout.info(f"\t{range_name_SBLo}, {range_name_Blind}, {range_name_SBHi}")
    
    def set_initial_errors(self, source:Optional["ROOT.RooArgSet"]=None):
        if not source:
            source = self.nuisance_parameters
    
        all_constraints = self.get_all_constraints()
        for nuis in source:
            nuis_name = nuis.GetName()
            prefit_variation, constraint_type, _ = self.inspect_constrained_nuisance_parameter(nuis, all_constraints)
            if constraint_type=='gaus':
                self.stdout.info(f'INFO: Changing error of {nuis_name} from {nuis.getError()} to {prefit_variation}')
                nuis.setError(prefit_variation)
                nuis.removeRange()    
        return None
    
    def get_poi(self, poi_name:Optional[str]=None, strict:bool=False):
        """Get POI variable by name
        
        Arguments
            poi_name: str
                name of POI to retrieve
            strict: bool
                require the variable to be defined in the POI list, throw error otherwise
        """
        if poi_name is None:
            poi = self.pois.first()
            self.stdout.info(f"INFO: POI name not specified. The first POI \"{poi.GetName()}\" is used by default.")
        else:
            poi = self.workspace.var(poi_name)
        if not poi:
            raise RuntimeError(f"workspace does not contain the variable \"{poi_name}\"")
        if strict and (poi not in list(self.pois)):
            raise RuntimeError(f"workspace variable \"{poi_name}\" is not part of the POIs")
        return poi
    
    def _load_obs_and_weight(self, obs_and_weight:Optional[Union["ROOT.RooArgSet",str]]=None, 
                             weight_var:Optional[Union["ROOT.RooRealVar",str]]=None):
        # get the weight variable
        if weight_var is None:
            weight_name = self._DEFAULT_NAMES_['weight']
            weight_var = self.workspace.var(weight_name)
            if not weight_var:
                weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
                getattr(self.workspace, "import")(weight_var)
        elif isinstance(weight_var, str):
            weight_var = self.workspace.var(weight_var)
            if not weight_var:
                raise RuntimeError('weight variable "{}" not found in workspace'.format(weight_var))
        elif not isinstance(weight_var, ROOT.RooRealVar):
            raise ValueError('weight variable must be of RooRealVar type')
                
        # get the obs_and_weight arg set
        if obs_and_weight is None:
            default_name = self._DEFAULT_NAMES_['dataset_args']
            obs_and_weight = self.workspace.set(default_name)
            if not obs_and_weight:
                obs_and_weight = ROOT.RooArgSet()
                obs_and_weight.add(self.observables)            
                obs_and_weight.add(weight_var)
                self.workspace.defineSet(default_name, obs_and_weight)
        elif isinstance(obs_and_weight, str):
            obs_and_weight = self.workspace.set(obs_and_weight)
            if not obs_and_weight:
                raise RuntimeError(f'named set "{obs_and_weight}" not found in workspace')
        elif not isinstance(obs_and_weight, ROOT.RooArgSet):
            raise ValueError('the argument "obs_and_weight" must be of RooArgSet type')
        return obs_and_weight, weight_var
    
    def import_object(self, obj):
        getattr(self.workspace, "import")(obj)
        
    @staticmethod
    def get_object_map(object_dict:Dict, object_name:str):
        if object_name not in ["RooDataSet", "RooAbsPdf"]:
            raise ValueError(f"unsupported object \"{object_name}\"")
        object_map = ROOT.std.map(f"string, {object_name}*")()
        object_map.keepalive = list()
        for c, d in object_dict.items():
            object_map.keepalive.append(d)
            object_map.insert(object_map.begin(), ROOT.std.pair(f"const string, {object_name}*")(c, d))
        return object_map
    
    @staticmethod
    def get_dataset_map(dataset_dict:Dict):
        dsmap = ROOT.std.map('string, RooDataSet*')()
        dsmap.keepalive = list()
        for c, d in dataset_dict.items():
            dsmap.keepalive.append(d)
            dsmap.insert(dsmap.begin(), ROOT.std.pair("const string, RooDataSet*")(c, d))
        return dsmap
    
    @staticmethod
    def get_pdf_map(pdf_dict:Dict):
        pdfmap = ROOT.std.map('string, RooAbsPdf*')()
        pdfmap.keepalive = list()
        for c, d in pdf_dict.items():
            pdfmap.keepalive.append(d)
            pdfmap.insert(pdfmap.begin(), ROOT.std.pair("const string, RooAbsPdf*")(c, d))
        return pdfmap
    
    def generate_asimov_from_pdf(self, name:str="asimovData", pdf:Optional["ROOT.RooAbsPdf"]=None,
                                 obs_and_weight:Optional[Union["ROOT.RooArgSet",str]]=None, 
                                 weight_var:Optional[Union["ROOT.RooRealVar",str]]=None,
                                 extra_args=None):
        
        pdf = pdf if pdf is not None else self.pdf
        if isinstance(pdf, ROOT.RooSimultaneous):
            raise ValueError("this method should not be called from a simultaneous pdf")
        
        obs_and_weight, weight_var = self._load_obs_and_weight(obs_and_weight, weight_var)
        
        # get the combined arg set for the asimov dataset
        arg_set = ROOT.RooArgSet()
        arg_set.add(obs_and_weight)
        if extra_args is not None:
            if isinstance(extra_args, list):
                for arg in extra_args:
                    arg_set.add(arg)
            else:
                arg_set.add(extra_args)
                
        asimov_data = ROOT.RooDataSet(name, name, arg_set, ROOT.RooFit.WeightVar(weight_var))
        
        # generate observables defined by the pdf associated with this state
        obs = pdf.getObservables(self.observables)
        target_obs = obs.first()
        expected_events = pdf.expectedEvents(obs)
        #print("INFO: Generating Asimov for pdf {}".format(pdf.GetName()))
        for i in range(target_obs.numBins()):
            target_obs.setBin(i)
            norm = pdf.getVal(obs)*target_obs.getBinWidth(i)
            n_events = norm*expected_events
            if n_events <= 0:
                self.stdout.warning("WARNING: Detected bin with zero expected events ({})! Please check"
                      "your inputs. Obs = {}, bin = {}".format(n_events, target_obs.GetName(), i))
            elif (n_events > 0) and (n_events < 1e18):
                self.stdout.debug("pdf={}, obs={}, bin={}, val={}".format(
                    pdf.GetName(), target_obs.GetName(), i, n_events))
                asimov_data.add(self.observables, n_events)
            else:
                raise RuntimeError(f"detected pdf bin with nan (pdf={pdf.GetName()},obs={target_obs.GetName()},bin={i})")

        if (asimov_data.sumEntries() != asimov_data.sumEntries()):
            raise RuntimeError("asimov data sum entries is nan")
        return asimov_data
    
    def match_globs(self):
        _, components, globs = self.pair_constraints(fmt="argset", base_component=True, sort=True)
        for component, glob in zip(components, globs):
            glob.setVal(component.getVal())
            self.stdout.debug("set glob {} to val {}".format(glob.GetName(), glob.getVal()))
        """
        for nuis, globs, pdf in zip(nuis_list, globs_list, pdf_list):
            pdf_class = pdf.ClassName()
            if pdf_class in ["RooGaussian", "RooBifurGauss"]:
                globs.setVal(nuis.getVal())
            elif pdf_class == "RooPoisson":            
                globs.setVal(nuis.getVal()*globs.getVal())
            else:
                raise RuntimeError(f"constraint term \"{pdf.GetName()}\" has unsupported type \"{pdf_class}\"")
            self.stdout.debug("set glob {} to val {}".format(globs.GetName(), globs.getVal()))
        """

    def generate_asimov(self, poi_name:Optional[str]=None, poi_val:Optional[float]=None, 
                        poi_profile:Optional[float]=None,
                        do_fit:bool=True,
                        modify_globs:bool=True,
                        do_import:bool=True,
                        asimov_name:Optional[str]=None,
                        asimov_snapshot:Optional[str]=None,
                        channel_asimov_name:Optional[str]=None,
                        dataset:Optional["ROOT.RooDataSet"]=None,
                        constraint_option:int=0,
                        restore_states:int=0,
                        minimizer_options:Optional[Dict]=None, 
                        nll_options:Optional[Union[Dict, List]]=None,
                        snapshot_names:Optional[Dict]=None):
        """
            Generate Asimov dataset.
            
            Note:
                Nominal (initial values) snapshots of nuisance parameters and global are saved
                as "nominalNuis" and "nominalGlobs" if not already exist. Conditional snapshots
                are saved as "conditionalNuis_{mu}" and "conditionalGlobs_{mu}" irrespective of
                whether nuisance parameter profiling is performed and whether conditional mle
                is used for the profiling. This is to faciliate the use case of Asymptotic limit
                calculation. The names of these snahpshots can be customized via the
                `snapshot_names` option.
        
            Arguments:
                poi_name: str
                    Name of the parameter of interest (POI).
                poi_val: (Optional) float
                    Generate asimov data with POI set at the specified value. If None, POI will be kept
                    at the post-fit value if a fitting is performed or the pre-fit value if no fitting
                    is performed.
                poi_profile: (Optional) float
                    Perform nuisance parameter profiling with POI set at the specified value. This option
                    is only effective if do_fit is set to True. If None, POI is set floating 
                    (i.e. unconditional maximum likelihood estimate). 
                do_fit: bool, default=True    
                    Perform nuisance parameter profiling with a fit to the given dataset.
                modify_globs: bool, default=True
                    Match the values of nuisance parameters and the corresponding global observables when
                    generating the asimov data. This is important for making sure the asimov data has the 
                    (conditional) minimal NLL.
                constraint_option: int, default=0
                    Customize the target of nuisance paramaters involved in the profiling.
                    Case 0: All nuisance parameters are allowed to float;
                    Case 1: Constrained nuisance parameters are fixed to 0. Unconstrained nuisrance
                            parameters are allowed to float.
                restore_states: int, default=0
                    Restore variable states at the end of asimov data generation.
                    Case 0: All variable states will be restored.
                    Case 1: Only global observable states will be restored.
                do_import: bool, default=True
                    Import the generated asimov data to the current workspace.
                asimov_name: (Optional) str
                    Name of the generated asimov dataset. If None, defaults to "asimovData_{mu}" where
                    `{mu}` will be replaced by the value of `poi_val`. Other keywords are: `{mu_cond}`
                    which is the the value of `poi_profile`.
                asimov_snapshot: (Optional) str
                    Name of the snapshot taken right after asimov data generation. If None, no snapshot
                    will be saved.
                channel_asimov_name: (Optional) str
                    Name of the asimov dataset in each category of a simultaneous pdf. If None,
                    defaults to "combAsimovData_{label}" where `{label}` will be replaced by the
                dataset: (Optional) ROOT.RooDataSet
                    Dataset based on which the negative log likelihood (NLL) is created for nuisance parameter
                    profiling. If None, default to self.data.
                minimizer_options: (Optional) dict
                    Options for minimization during nuisance parameter profiling. If None, defaults to
                    ExtendedMinimizer._DEFAULT_MINIMIZER_OPTION_
                nll_options: (Optional) dict, list
                    Options for NLL creation during nuisance parameter profiling. If None, defaults to
                    ExtendedMinimizer._DEFAULT_NLL_OPTION_
                snapshot_names: (Optional) dict
                    A dictionary containing a map of the snapshot type and the snapshot names. The default
                    namings are stored in ExtendedModel._DEFAULT_NAMES_.
        """
        # define simplified ws variable names
        ws = self.workspace
        all_globs = self.global_observables
        all_nuis  = self.nuisance_parameters
        
        # define names used for various objects
        names = copy.deepcopy(self._DEFAULT_NAMES_)
        if snapshot_names is not None:
            names.update(snapshot_names)
        if asimov_name is not None:
            names['asimov'] = asimov_name
            names['asimov_no_poi'] = asimov_name
        if channel_asimov_name is not None:
            names['channel_asimov'] = channel_asimov_name
        nom_vars_name = names['nominal_vars']
        nom_glob_name = names['nominal_globs']
        nom_nuis_name = names['nominal_nuis']
        con_glob_name = names['conditional_globs']
        con_nuis_name = names['conditional_nuis']

        if poi_name is None:
            poi = None
        else:
            poi = self.get_poi(poi_name)
        
        # take snapshot of initial states of all variables
        ws.saveSnapshot(nom_vars_name, self.workspace.allVars())
        if not ws.getSnapshot(nom_glob_name):
            self.stdout.info('INFO: Saving snapshot "{}"'.format(nom_glob_name))
            ws.saveSnapshot(nom_glob_name, all_globs)
        if not ws.getSnapshot(nom_nuis_name):
            self.stdout.info('INFO: Saving snapshot "{}"'.format(nom_nuis_name))
            ws.saveSnapshot(nom_nuis_name, all_nuis)
        
        if do_fit:
            from quickstats.components import ExtendedMinimizer
            if dataset is None:
                dataset = self.data
            minimizer = ExtendedMinimizer("Minimizer", self.pdf, dataset)
            if minimizer_options is None:
                minimizer_options = copy.deepcopy(minimizer._DEFAULT_MINIMIZER_OPTION_)
            if nll_options is None:
                nll_options = copy.deepcopy(minimizer._DEFAULT_NLL_OPTION_)
            minimizer.configure(**minimizer_options)
            if constraint_option == 0:
                pass
            elif constraint_option == 1:
                self.set_constrained_nuisance_parameters_to_nominal()
            else:
                raise ValueError(f"unsupported constraint option: {constraint_option}")
            if isinstance(nll_options, dict):
                minimizer.configure_nll(**nll_options)
            elif isinstance(nll_options, list):
                minimizer.set_nll_commands(nll_options)
            else:
                raise ValueError(f"unsupported nll options format")
            if poi:
                if poi_profile is not None:
                    # conditional mle
                    poi.setVal(poi_profile)
                    poi.setConstant(1)
                else:
                    # unconditional mle
                    poi.setConstant(0)
            minimizer.minimize()
        
        if poi:
            if poi_val is not None:
                poi.setVal(poi_val)
            poi.setConstant(0)
            poi_val = poi.getVal()
        
        # match values of global observables to the corresponding NPs
        if modify_globs:
            self.match_globs()

        if poi:
            if do_fit:
                ws.saveSnapshot(con_glob_name.format(mu=pretty_value(poi_profile)), all_globs)
                ws.saveSnapshot(con_nuis_name.format(mu=pretty_value(poi_profile)), all_nuis)
            else:
                ws.saveSnapshot(con_glob_name.format(mu=pretty_value(poi_val)), all_globs)
                ws.saveSnapshot(con_nuis_name.format(mu=pretty_value(poi_val)), all_nuis)

            asimov_data_name = names['asimov'].format(mu=pretty_value(poi_val),
                                                      mu_cond=pretty_value(poi_profile))
        else:
            asimov_data_name = names['asimov_no_poi']
            
        channel_asimov_data_name = names['channel_asimov']
        sim_pdf = self.pdf
        if not isinstance(sim_pdf, ROOT.RooSimultaneous):
            asimov_data = self.generate_asimov_from_pdf(asimov_data_name, sim_pdf)
        else:
            asimov_data_map = {}
            channel_cat = sim_pdf.indexCat()
            n_cat = channel_cat.size()
            for i in range(n_cat):
                channel_cat.setIndex(i)
                label = channel_cat.getLabel()
                pdf_cat = sim_pdf.getPdf(label)
                name = channel_asimov_data_name.format(index=i, label=label)
                asimov_data_map[label] = self.generate_asimov_from_pdf(name, pdf_cat, extra_args=channel_cat)

            obs_and_weight, weight_var = self._load_obs_and_weight()
            dataset_map = ExtendedModel.get_dataset_map(asimov_data_map)
            asimov_data = ROOT.RooDataSet(asimov_data_name, asimov_data_name, 
                                          ROOT.RooArgSet(obs_and_weight, channel_cat),
                                          ROOT.RooFit.Index(channel_cat),
                                          ROOT.RooFit.Import(dataset_map),
                                          ROOT.RooFit.WeightVar(weight_var))
        if do_import:
            getattr(ws, "import")(asimov_data)
            self.stdout.info(f'INFO: Generated Asimov Dataset \"{asimov_data_name}\"')
            
        if asimov_snapshot is not None:
            self.stdout.info('INFO: Saving snapshot "{}"'.format(asimov_snapshot))
            ws.saveSnapshot(asimov_snapshot, self.workspace.allVars())
    
        if restore_states == 0:
            # load back a snapshot of all varaible's initial states
            ws.loadSnapshot(nom_vars_name)
        elif restore_states == 1:
            # load back a snapshot of the initial global observable states
            ws.loadSnapshot(nom_glob_name)
        elif restore_states == 2:
            pass
        else:
            raise ValueError(f"unsupported restore state option \"{restore_states}\"")
        
        return asimov_data
    
    def generate_toys(self, n_toys:int=1, seed:Union[int, List[int]]=0, 
                      binned:bool=True, randomize_globs:bool=True,
                      do_import:bool=True, name="toyData_{index}_seed_{seed}"):
        if n_toys > 1:
            if seed == 0:
                seeds = [0] * n_toys
            elif (not isinstance(seed, (list, np.ndarray, range))) or (len(seed) != n_toys):
                raise ValueError("seed must be a list of size n_toys if seed != 0")
            else:
                seeds = seed
                
        ws = self.workspace
        # take snapshot of initial states of all variables
        self.workspace.saveSnapshot("tmp", self.workspace.allVars())
        
        if binned:
            if self.pdf.ClassName() == "RooSimultaneous":
                index_cat = self.pdf.indexCat()
                for cat in index_cat:
                    pdf_i = self.pdf.getPdf(cat.first)
                    pdf_i.setAttribute("GenerateToys::Binned")
            else:
                self.pdf.setAttribute("GenerateToys::Binned")
        
        toys = []
        args = [self.observables, ROOT.RooFit.Extended(), ROOT.RooFit.AutoBinned(True)]
        if binned:
            args.append(ROOT.RooFit.GenBinned("GenerateToys::Binned"))
        
        for i in range(n_toys):
            if randomize_globs:
                self.randomize_globs(self.pdf, self.global_observables, seeds[i])
            toy = self.pdf.generate(*args)
            toy_name = name.format(seed=seeds[i], index=i)
            toy.SetName(toy_name)
            if do_import:
                if ws.data(toy_name):
                    raise RuntimeError(f"attempt to overwrite existing dataset `{toy_name}`")
                getattr(ws, "import")(toy)
                self.stdout.info(f'INFO: Generated toy dataset "{toy_name}"')
            toys.append(toy)
        
        ws.loadSnapshot("tmp")
        
        return toys
    
    def save(self, fname:str, recreate:bool=True):
        """
        # buggy, model config is messed up
        new_ws = ROOT.RooWorkspace(self.workspace)
        new_ws.writeToFile(fname, recreate)
        """
        self.workspace.writeToFile(fname, recreate)
    
    @semistaticmethod
    def load_ws(self, fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None):
        if not os.path.exists(fname):
            raise FileNotFoundError('workspace file {} does not exist'.format(fname))
        file = ROOT.TFile(fname)
        if (not file):
            raise RuntimeError("Something went wrong while loading the root file: {}".format(fname))        
        # load workspace
        if ws_name is None:
            ws_names = [i.GetName() for i in file.GetListOfKeys() if i.GetClassName() == 'RooWorkspace']
            if not ws_names:
                raise RuntimeError("No workspaces found in the root file: {}".format(fname))
            if len(ws_names) > 1:
                self.stdout.warning("WARNING: Found multiple workspace instances from the root file: {}. Available workspaces"
                      " are \"{}\". Will choose the first one by default".format(fname, ','.join(ws_names)))
            ws_name = ws_names[0]
        ws = file.Get(ws_name)
        if not ws:
            raise RuntimeError('Failed to load workspace: "{}"'.format(ws_name))
        # load model config
        if mc_name is None:
            mc_names = [i.GetName() for i in ws.allGenericObjects() if 'ModelConfig' in i.ClassName()]
            if not mc_names:
                raise RuntimeError("no ModelConfig object found in the workspace: {}".format(ws_name))
            if len(mc_names) > 1:
                self.stdout.warning("WARNING: Found multiple ModelConfig instances from the workspace: {}. "
                      "Available ModelConfigs are \"{}\". "
                      "Will choose the first one by default".format(ws_name, ','.join(mc_names)))
            mc_name = mc_names[0]     
        mc = ws.obj(mc_name)
        if not mc:
            raise RuntimeError('Failed to load model config "{}"'.format(mc_name))
        return file, ws, mc
    
    def get_category_map(self, pdf=None):
        if pdf is None:
            pdf = self.pdf
        if not isinstance(pdf, ROOT.RooSimultaneous):
            raise ValueError("input pdf is not a simultaneous pdf")            
        category_map = {}
        index_cat = pdf.indexCat()
        n_cat = index_cat.size()
        for i in range(n_cat):
            index_cat.setIndex(i)
            label = index_cat.getLabel()
            pdf_cat = pdf.getPdf(label)
            obs = pdf_cat.getObservables(self.observables)
            target_obs = obs.first()
            category_map[label] = {}
            category_map[label]['index'] = i
            category_map[label]['pdf'] = pdf_cat.GetName()
            category_map[label]['observable'] = target_obs.GetName()
            bin_range = target_obs.getRange()
            category_map[label]['bin_range'] = (bin_range.first, bin_range.second)
            category_map[label]['bins'] = target_obs.getBins()
        return category_map
    
    @staticmethod
    def get_dataset_values(dataset:ROOT.RooDataSet):
        return RooDataSet.to_numpy(dataset)
    
    def _get_new_binnings(self, bins:Optional[Union[Dict, int]]=None):
        category_map = self.get_category_map()
        binnings = {}
        for category in category_map:
            binnings[category] = {}
            bin_range = category_map[category]['bin_range']
            if bins is None:
                _bins = category_map[category]['bins']
            elif isinstance(bins, dict):
                _bins = bins.get(category, None)
                if _bins is None:
                    raise RuntimeError(f"binning not specified for the category \"{category}\"")
            elif isinstance(bins, int):
                _bins = bins
            else:
                raise RuntimeError(f"invalid binning format: {bins}")
            bin_width = round((bin_range[1] - bin_range[0]) / _bins, 8)
            binnings[category]['bin_range'] = bin_range
            binnings[category]['bins'] = _bins
            binnings[category]['bin_width'] = bin_width
        return binnings
    
    def get_dataset_distributions(self, dataset, n_bins:Optional[Union[Dict, int]]=None):
        distributions = {}
        dataset_values = self.get_dataset_values(dataset)
        if 'label' not in dataset_values:
            raise RuntimeError("no categories defined in the dataset")
        category_map = self.get_category_map()
        binnings = self._get_new_binnings(n_bins)
        for cat in category_map:
            distributions[cat] = {}
            observable = category_map[cat]['observable']
            if observable not in dataset_values:
                raise RuntimeError(f"no data associated with the observable \"{observable}\" found in the dataset")
            distributions[cat]['observable'] = observable
            mask = (dataset_values['label'] == cat)
            x = dataset_values[observable][mask]
            ind = np.argsort(x)
            x = x[ind]
            y = dataset_values['weight'][mask][ind]
            default_bins = category_map[cat]['bins']
            ghost  = False
            if np.all(y == 1.):
                binned = False
            else:
                # check if the event with non-unity weight are from the ghost
                y_with_ghost_removed = y[y > 1e-8]
                if np.all(y_with_ghost_removed == 1.):
                    binned = False
                    ghost  = True
                elif len(x) == default_bins:
                    binned = True
                else:
                    # check for blinded histogram
                    nbins     = binnings[cat]['bins']
                    bin_range = binnings[cat]['bin_range']
                    correct_bins = get_bins_given_edges(bin_range[0], bin_range[1], nbins)
                    issubset = array_issubset(correct_bins, x)
                    if issubset:
                        binned = True
                        missing_bins   = np.setdiff1d(correct_bins, x)
                        # fill missing bins with zero values
                        missing_values = np.zeros(missing_bins.shape[0])
                        x = np.concatenate([x, missing_bins])
                        y = np.concatenate([y, missing_values])
                        idx = np.argsort(x)
                        x = x[idx]
                        y = y[idx]
                    else:
                        raise RuntimeError(f"detected dataset with invalid binning")
            bins = binnings[cat]['bins']
            if binned:
                if  (bins != default_bins):
                    raise RuntimeError(f"cannot change binning of binned dataset ({dataset.GetName()}, cat = {cat}): "
                                       f"original binning = {default_bins}, requested binning = {bins}")
                distributions[cat]['x'] = x
                distributions[cat]['y'] = y
            else:
                bin_range = binnings[cat]['bin_range']
                if not ghost:
                    hist, bin_edges = np.histogram(x, bins=bins, range=(bin_range[0], bin_range[1]))
                    bin_centers = (bin_edges[1:] + bin_edges[:-1])/2
                    distributions[cat]['x'] = bin_centers
                    distributions[cat]['y'] = hist
                else:
                    ghost_idx = y < 1e-8
                    hist, bin_edges = np.histogram(x[~ghost_idx], bins=bins, range=(bin_range[0], bin_range[1]))
                    hist_g, _ = np.histogram(x[ghost_idx], bins=bins, range=(bin_range[0], bin_range[1]), weights=y[ghost_idx])
                    bin_centers = (bin_edges[1:] + bin_edges[:-1])/2
                    distributions[cat]['x'] = bin_centers
                    distributions[cat]['y'] = hist + hist_g
                bin_errors = TH1.GetPoissonError(distributions[cat]['y'])
                distributions[cat]['yerrlo'] = bin_errors['lo']
                distributions[cat]['yerrhi'] = bin_errors['hi']
        return distributions
    
    @semistaticmethod
    def get_simul_pdf_distributions(self, pdf, observables, n_bins:Optional[Union[Dict, int]]=None):
        if not isinstance(pdf, ROOT.RooSimultaneous):
            raise ValueError("input pdf is not a simultaneous pdf")
        distributions = {}
        channel_cat = pdf.indexCat()
        n_cat = channel_cat.size()
        binnings = self._get_new_binnings(n_bins)
        for i in range(n_cat):
            channel_cat.setIndex(i)
            label = channel_cat.getLabel()
            pdf_cat = pdf.getPdf(label)
            obs = pdf_cat.getObservables(observables)
            target_obs = obs.first()
            obs_name = target_obs.GetName()
            distributions[label] = {'x':[], 'y':[], 'observable': obs_name}
            if n_bins is None:
                n_bins = target_obs.numBins()
            bins = binnings[label]['bins']
            bin_width = binnings[label]['bin_width']
            h = pdf_cat.createHistogram(target_obs.GetName(), bins)
            py_h = TH1(h)
            distributions[label]['x'] = py_h.bin_center
            distributions[label]['y'] = py_h.bin_content * bin_width
            # free memory to avoid memory leak
            h.Delete()
            """
            expected_events = pdf_cat.expectedEvents(obs)
            for i in range(n_bins):
                target_obs.setBin(i)
                norm = pdf_cat.getVal(obs)*target_obs.getBinWidth(i)
                n_events = norm*expected_events
                bin_value = target_obs.getVal()
                if n_events <= 0:
                    self.stdout.warning("WARNING: Detected bin with zero expected events ({})! "
                                    "Please check your inputs. Obs = {}, bin = {}".format(
                                    n_events, target_obs.GetName(), i))
                elif (n_events > 0) and (n_events < 1e18):
                    distributions[label]['x'].append(bin_value)
                    distributions[label]['y'].append(n_events)
                else:
                    raise RuntimeError(f"detected pdf bin with nan (pdf={pdf.GetName()},obs={target_obs.GetName()},bin={i})")
            """
        return distributions
    
    def get_distributions(self, n_bins:Optional[Union[Dict, int]]=None):
        return self.get_simul_pdf_distributions(self.pdf, self.observables, n_bins=n_bins)
    
    def get_categories(self):
        return list(self.get_category_map())
    
    def get_collected_distributions(self, current_distributions=True,
                                    datasets:Optional[Union[List[str],List[ROOT.RooDataSet]]]=None,
                                    snapshots:Optional[List[str]]=None,
                                    n_bins:Optional[Union[Dict, int]]=None):
        collected_distributions = {}
                
        if datasets is not None:
            for dataset in datasets:
                if isinstance(dataset, str):
                    dataset_name = dataset
                    dataset = self.workspace.data(dataset)
                    if not dataset:
                        raise ValueError(f"dataset \"{dataset_name}\" does not exist")
                dataset_name = dataset.GetName()
                distributions = self.get_dataset_distributions(dataset, n_bins=n_bins)
                for category in distributions:
                    if category not in collected_distributions:
                        collected_distributions[category] = {}
                    collected_distributions[category][dataset_name] = distributions[category]

        if current_distributions:
            distributions = self.get_distributions(n_bins=n_bins)
            for category in distributions:
                if category not in collected_distributions:
                    collected_distributions[category] = {}
                collected_distributions[category]['Current'] = distributions[category]

        if snapshots is not None:
            self.workspace.saveSnapshot("tmp", self.workspace.allVars())
            try:
                for snapshot in snapshots:
                    exist = self.workspace.loadSnapshot(snapshot)
                    if not exist:
                        raise RuntimeError("snapshot \"{}\" not found in workspace".format(snapshot))
                    distributions = self.get_distributions(n_bins=n_bins)
                    for category in distributions:
                        if category not in collected_distributions:
                            collected_distributions[category] = {}
                        collected_distributions[category][snapshot] = distributions[category]
            finally:
                self.workspace.loadSnapshot("tmp")
        return collected_distributions
            
    def plot_distributions(self, categories:Optional[List[str]]=None, current_distributions=True, 
                           datasets:Optional[Union[List[str],List[ROOT.RooDataSet]]]=None,
                           snapshots:Optional[Union[List[str], List[ROOT.RooArgSet]]]=None,
                           n_bins:Optional[Union[Dict, int]]=None, discriminant:Optional[str]=None,
                           unit:Optional[str]=None, blind:bool=False, show_errorbar:bool=True,
                           comparison_options:Optional[Dict]=None, save_as:Optional[str]=None, **kwargs):
        from quickstats.plots import PdfDistributionPlot
        category_map = self.get_category_map()
        if categories is None:
            categories = list(category_map)
        for category in categories:
            if category not in category_map:
                raise ValueError("category \"{}\" not found in workspace".format(category))
        collected_distributions = self.get_collected_distributions(current_distributions,
                                                                   datasets, snapshots=snapshots,
                                                                   n_bins=n_bins)
        if save_as is not None:
            from matplotlib.backends.backend_pdf import PdfPages
            pdf = PdfPages(save_as)
        else:
            pdf = None
            
        if blind:
            all_blind_range = self.get_blind_range()
        else:
            all_blind_range = {}

        for i, category in enumerate(categories):
            obs_name = category_map[category]['observable']
            if discriminant is None:
                xlabel = obs_name
            else:
                #xlabel = f"{discriminant}_{category}"
                xlabel = f"{discriminant} (category {category})"
            binnings  = self._get_new_binnings(n_bins)
            bin_width = pretty_value(binnings[category]['bin_width'])
            ylabel    = f"Events / {bin_width}"
            if unit is not None:
                xlabel = f"{xlabel} [{unit}]"
                ylabel = f"{ylabel} {unit}"
                
            blind_range = all_blind_range.get(obs_name, None)
            
            plotter = PdfDistributionPlot(collected_distributions[category], 
                                          figure_index=i, **kwargs)
            ax = plotter.draw(xlabel=xlabel, ylabel=ylabel, 
                              blind_range=blind_range,
                              show_errorbar=show_errorbar,
                              comparison_options=comparison_options)
            if pdf is not None:
                pdf.savefig(bbox_inches="tight")
        if pdf is not None:
            pdf.close()
        return None
    
    def get_variables(self, variable_type:Union[str, WSVariables], sort:bool=True):
        _variable_type = WSVariables.parse(variable_type)
        if _variable_type == WSVariables.VARIABLES:
            variables = self.workspace.allVars()
        elif _variable_type == WSVariables.OBSERVABLES:
            variables = self.observables
        elif _variable_type == WSVariables.POIS:
            variables = self.pois
        elif _variable_type == WSVariables.GLOBAL_OBSERVABLES:
            variables = self.global_observables
        elif _variable_type == WSVariables.NUISANCE_PARAMETERS:
            variables = self.nuisance_parameters
        elif _variable_type == WSVariables.CONSTRAINED_NUISANCE_PARAMETERS:
            variables = RooArgSet.from_list(self.get_constrained_nuisance_parameters())
        elif _variable_type == WSVariables.UNCONSTRAINED_NUISANCE_PARAMETERS:
            variables = RooArgSet.from_list(self.get_unconstrained_nuisance_parameters())
        elif _variable_type == WSVariables.CONSTRAINTS:
            nuis_list, glob_list, pdf_list = self.pair_constraints(sort=sort)
            return RooArgSet.from_list(nuis_list), RooArgSet.from_list(glob_list), RooArgSet.from_list(pdf_list)
        elif _variable_type == WSVariables.AUXILIARY:
            variables           = self.get_variables("variables")
            pois                = self.get_variables("pois")
            nuisance_parameters = self.get_variables("nuisance_parameters")
            global_observables  = self.get_variables("global_observables")
            observables         = self.get_variables("observables")
            variables.remove(pois)
            variables.remove(nuisance_parameters)
            variables.remove(global_observables)
            variables.remove(observables)
        elif _variable_type == WSVariables.NON_CONSTRAINT_VARIABLES:
            variables           = self.get_variables("variables")
            nuisance_parameters = self.get_variables("nuisance_parameters")
            global_observables  = self.get_variables("global_observables")
            observables         = self.get_variables("observables")
            variables.remove(nuisance_parameters)
            variables.remove(global_observables)
            variables.remove(observables)
        elif _variable_type == WSVariables.CORE:
            variables = ROOT.RooArgSet()
            variables.add(self.nuisance_parameters)
            variables.add(self.global_observables)
            variables.add(self.pois)
        else:
            raise ValueError(f"unknown variable type \"{variable_type}\"")
        if sort:
            return RooArgSet.sort(variables)
        return variables
    
    def as_dataframe(self, variable_type:Union[str, WSVariables, ROOT.RooArgSet],
                     asym_error:bool=False):
        if isinstance(variable_type, ROOT.RooArgSet):
            vcollection = variable_type
        else:
            _variable_type = WSVariables.parse(variable_type)
            # for the special case of displaying constrain terms
            # will print the tuple of names of NP, Global Observables and Constrain Pdf
            if _variable_type == WSVariables.CONSTRAINTS:
                data = self.pair_constraints(to_str=True, fmt="dict")
                import pandas as pd
                df = pd.DataFrame(data).rename(columns={'pdf': 'constraint pdf',
                                                        'nuis': 'nuisance parameters',
                                                        'globs': 'global observables'})
                return df
            else:
                vcollection = self.get_variables(_variable_type)
        df = variable_collection_to_dataframe(vcollection, asym_error=asym_error)
        return df
    
    def rename_dataset(self, rename_map:Dict):
        for old_name, new_name in rename_map.items():
            if old_name == new_name:
                continue
            dataset = self.workspace.data(old_name)
            if not dataset:
                raise RuntimeError(f"dataset \"{old_name}\" not found in the workspace")
            check_dataset = self.workspace.data(new_name)
            if check_dataset:
                raise RuntimeError(f"cannot rename dataset from \"{old_name}\" to \"{new_name}\": "
                                   f"the dataset \"{new_name}\" already exists in the workspace")
            dataset.SetName(new_name)
    
    @staticmethod
    def _format_category_summary(category_name:str, category_map:Dict):
        observable = category_map['observable']
        bin_range = category_map['bin_range']
        bins = category_map['bins']
        summary_str = f"{category_name} (observable = {observable}, range = [{bin_range[0]}, {bin_range[1]}], bins = {bins})"
        return summary_str
        
    def print_summary(self, items:Optional[List]=None, suppress_print:bool=False, detailed:bool=True,
                      include_patterns:Optional[List]=None, exclude_patterns:Optional[List]=None,
                      save_as:Optional[str]=None):
        if items is None:
            items = ['workspace', 'dataset', 'snapshot', 'category',
                     'poi', 'detailed_nuisance_parameter']
        summary_str = ""
        # workspace
        if 'workspace' in items:
            summary_str += f"Workspace:\n"
            summary_str += f"\t{self.workspace.GetName()}\n"
        # datasets
        if 'dataset' in items:
            datasets = self.workspace.allData()
            summary_str += f"Datasets ({len(datasets)}):\n"
            summary_str += "".join([f"\t{obs.GetName()}\n" for obs in datasets])
        # snapshots
        if ('snapshot' in items):
            if (quickstats.root_version >= (6, 26, 0)):
                snapshots = self.workspace.getSnapshots()
                summary_str += f"Snapshots ({len(snapshots)}):\n"
                summary_str += "".join([f"\t{snap.GetName()}\n" for snap in snapshots])
            else:
                self.stdout.warning("WARNING: Snapshot listing is only available after ROOT 6.26/00")
        # categories
        if 'category' in items:
            if isinstance(self.pdf, ROOT.RooSimultaneous):
                category_map = self.get_category_map()
                n_cat = len(category_map)
                summary_str += f"Categories ({n_cat}):\n"
                for category in category_map:
                    summary_str += "\t" + self._format_category_summary(category, category_map[category]) + "\n"
        # pois, NPs
        param_strs     = []
        param_sets     = []
        if 'poi' in items:
            pois = self.pois            
            param_strs.append('POIs')
            param_sets.append(pois)
        if 'detailed_nuisance_parameter' in items:
            constrained_nps = self.get_constrained_nuisance_parameters()
            unconstrained_nps = self.get_unconstrained_nuisance_parameters(constrained_nps)            
            param_strs += ['Constrained NPs', 'Unconstrained NPs']
            param_sets += [constrained_nps, unconstrained_nps]
        elif 'nuisance_parameter' in items:
            param_strs += ['NPs']
            param_sets += [self.nuisance_parameters]
        if 'global_observable' in items:
            param_strs += ['Global Observables']
            param_sets += [self.global_observables]
        if 'auxiliary' in items:
            param_strs += ['Auxiliary Parameters']
            param_sets += [self.get_variables('auxiliary')]            
        for pstr, pset in zip(param_strs, param_sets):
            summary_str += f"{pstr} ({len(pset)}):\n"
            param_names = [p.GetName() for p in pset]
            param_names_to_include = param_names.copy()
            if include_patterns is not None:
                param_names_to_include = str_list_filter(param_names_to_include, include_patterns, inclusive=True)
            if exclude_patterns is not None:
                param_names_to_include = str_list_filter(param_names_to_include, exclude_patterns, inclusive=False)
            param_index = np.in1d(param_names, param_names_to_include).nonzero()
            pset = np.array(pset)[param_index]
            data = [get_variable_attributes(p) for p in pset]
            data = sorted(data, key=lambda d: d['name'])
            if detailed:
                for d in data:
                    name   = d['name']
                    value  = d['value']
                    vmin   = d['min']
                    vmax   = d['max']
                    const_str = "C" if d['is_constant'] else "F"
                    summary_str += f"\t{name} = {value} [{vmin}, {vmax}] {const_str}\n"
            else:
                for d in data:
                    name = d['name']
                    summary_str += f"\t{name}\n"
        if not suppress_print:
            self.stdout.info(summary_str)
        if save_as is not None:
            with open(save_as, "w") as f:
                f.write(summary_str)