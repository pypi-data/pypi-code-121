from typing import Optional, Union, List

from quickstats.components import AbstractObject, ExtendedModel, ExtendedMinimizer
from quickstats.components.basics import WSVariables
from quickstats.utils.common_utils import get_class_that_defined_method
import ROOT

class AnalysisObject(AbstractObject):
    
    kInitialSnapshotName = "initialSnapshot"
    kCurrentSnapshotName = "currentSnapshot"
    kTempSnapshotName    = "tmpSnapshot"
    
    def __init__(self, filename:Optional[str]=None, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:str='combData', binned_likelihood:bool=True,
                 fix_param:str='', profile_param:str='', ws_name:Optional[str]=None, 
                 mc_name:Optional[str]=None, snapshot_name:Optional[Union[List[str], str]]=None,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', precision:float=0.001, 
                 eps:float=1.0, retry:int=1, strategy:int=1, print_level:int=-1, timer:bool=False,
                 num_cpu:int=1, offset:bool=True, optimize:int=2, eigen:bool=False, hesse:bool=False,
                 fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1, 
                 max_iters:int=-1, constrain_nuis:bool=True, batch_mode:bool=False,
                 int_bin_precision:float=-1., preset_param:bool=False,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)    
        self.model = None
        self.minimizer = None
        self._use_blind_range = False
        
        if filename is not None:
            self.setup_model(filename, data_name, binned_likelihood, ws_name, mc_name, 
                             snapshot_name, fix_cache, fix_multi, verbosity=verbosity)
            self.save_snapshot(self.kInitialSnapshotName)
            self.set_poi(poi_name)
            if preset_param:
                self.preset_parameters()
            self.setup_parameters(fix_param, profile_param, update_snapshot=True)
            self.setup_minimizer(minimizer_type, minimizer_algo, precision, eps, retry, strategy,
                                 num_cpu, offset, optimize, eigen, hesse, max_calls, max_iters, print_level,
                                 timer, constrain_nuis, batch_mode, int_bin_precision,
                                 verbosity=verbosity)
            self.sanity_check()
        
    def sanity_check(self):
        aux_vars = self.model.get_variables("auxiliary")
        floating_aux_vars = [v.GetName() for v in aux_vars if not v.isConstant()]
        if len(floating_aux_vars) > 0:
            self.stdout.warning("WARNING: The following auxiliary variables (variables that are not "
                                "part of the POIs, observables, nuisance parameters and global "
                                f"observables) are floating: {','.join(floating_aux_vars)}. If this is "
                                "not intended, please make sure to fix them before fitting.", "red")            
    
    def preset_parameters(self):
        ROOT.RooStats.SetAllConstant(self.model.global_observables, True)
        #ROOT.RooStats.SetAllConstant(self.model.nuisance_parameters, False)
        ROOT.RooStats.SetAllConstant(self.model.pois, True)
        self.stdout.info("INFO: Preset POIs as constant parameters.")
        #self.stdout.info("INFO: Preset nuisance parameters as floating parameters.")
        self.stdout.info("INFO: Preset global observables as constant parameters.")
    
    @property
    def use_blind_range(self):
        return self._use_blind_range
    
    @property
    def minimizer_options(self):
        return self.minimizer.config
    
    @property
    def nll_commands(self):
        return self.minimizer.nll_commands
    
    # black magic
    def _inherit_init(self, init_func, **kwargs):
        import inspect
        this_parameters = list(inspect.signature(AnalysisObject.__init__).parameters)
        if "self" in this_parameters:
            this_parameters.remove("self")
        that_parameters = list(inspect.signature(init_func).parameters)
        is_calling_this = set(this_parameters) == set(that_parameters)
        if is_calling_this:
            init_func(**kwargs)
        else:
            that_kwargs = {k:v for k,v in kwargs.items() if k in that_parameters}
            this_kwargs = {k:v for k,v in kwargs.items() if k not in that_parameters}
            init_func(config=this_kwargs, **that_kwargs)

    def set_poi(self, poi_name:Optional[Union[str, List[str]]]=None):
        # multi POI case
        if isinstance(poi_name, list):
            self.poi = ROOT.RooArgSet()
            true_poi_names = []
            # remove duplicates
            poi_name = list(set(poi_name))
            for pname in poi_name:
                poi = self.model.get_poi(pname)
                self.poi.add(poi)
                true_poi_names.append(poi.GetName())
            if true_poi_names:
                self.stdout.info('INFO: POIs set to {}'.format(", ".join([f"\"{name}\"" for name in true_poi_names])))
        else:
            self.poi = self.model.get_poi(poi_name)
            if poi_name is not None:
                self.stdout.info('INFO: POI set to "{}"'.format(poi_name))            
        
    def setup_model(self, filename, data_name='combData', binned_likelihood:bool=True, 
                    ws_name:Optional[str]=None, mc_name:Optional[str]=None, 
                    snapshot_name:Optional[str]=None, fix_cache:bool=True, 
                    fix_multi:bool=True, verbosity:Optional[Union[int, str]]="INFO"):
        model = ExtendedModel(fname=filename, ws_name=ws_name, mc_name=mc_name, data_name=data_name, 
                              snapshot_name=snapshot_name, binned_likelihood=binned_likelihood,
                              fix_cache=fix_cache, fix_multi=fix_multi, verbosity=verbosity)
        self.model = model
    
    def setup_parameters(self, fix_param:str='', profile_param:str='', update_snapshot:bool=True):
        if not self.model:
            raise RuntimeError('uninitialized analysis object')
        fixed_parameters = []
        profiled_parameters = []
        if fix_param:
            fixed_parameters = self.model.fix_parameters(fix_param)
        if profile_param:
            profiled_parameters = self.model.profile_parameters(profile_param)
        if update_snapshot:
            self.save_snapshot(self.kCurrentSnapshotName)
        self._check_poi_setup(fixed_parameters, profiled_parameters)
    
    def _check_poi_setup(self, fixed_parameters:List, profiled_parameters:List):
        # pois defined in workspace
        ws_pois  = self.model.pois
        # pois defined in this analysis
        ana_pois = ROOT.RooArgSet(self.poi)
        if ana_pois.size() == 0:
            return None
        aux_pois = ROOT.RooArgSet(ws_pois)
        aux_pois.remove(ana_pois)
        for profiled_param in profiled_parameters:
            if aux_pois.contains(profiled_param):
                param_name = profiled_param.GetName()
                self.stdout.warning(f"WARNING: Attemping to profile the parameter \"{param_name}\" which is a "
                                    f"POI defined in the workspace but not a POI used in this study. This "
                                    f"parameter will still be fixed during likelihood fit / limit setting. "
                                    f"Please designate the parameter as a POI in this study if intended.", "red")
        for fixed_param in fixed_parameters:
            if ana_pois.contains(fixed_param):
                param_name = fixed_param.GetName()
                self.stdout.warning(f"WARNING: Attemping to fix the parameter \"{param_name}\" which is a "
                                    f"POI used in this study. This parameter will still be floated during "
                                    f"unconditional likelihood fit / limit setting.", "red")
            
    def setup_minimizer(self, minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', 
                        precision:float=0.001, eps:float=1.0, retry:int=1, strategy:int=0, 
                        num_cpu:int=1, offset:bool=True, optimize:bool=True, eigen:bool=False,
                        hesse:bool=False, max_calls:int=-1, max_iters:int=-1, print_level:int=-1,
                        timer:bool=False, constrain_nuis:bool=True, batch_mode:bool=False,
                        int_bin_precision:float=-1., verbosity:Optional[Union[int, str]]="INFO"):
        
        minimizer = ExtendedMinimizer("Minimizer", self.model.pdf, self.model.data, verbosity=verbosity)
        
        nll_options = {
            "num_cpu": num_cpu,
            "offset": offset,
            "batch_mode": batch_mode,
            "int_bin_precision": int_bin_precision
        }
        if constrain_nuis:
            nll_options['constrain'] = self.model.nuisance_parameters
            nll_options['global_observables'] = self.model.global_observables
            conditional_obs = self.model.model_config.GetConditionalObservables()
            if conditional_obs:
                nll_options['conditional_observables'] = conditional_obs
            #nll_commands.append(ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet()))
        
        minimizer_options = {
            'minimizer_type'   : minimizer_type,
            'minimizer_algo'   : minimizer_algo,
            'default_strategy' : strategy,
            'opt_const'        : optimize,
            'precision'        : precision,
            'eps'              : eps,
            'retry'            : retry,
            'eigen'            : eigen,
            'hesse'            : hesse,
            'max_calls'        : max_calls,
            'max_iters'        : max_iters,
            'print_level'      : print_level,
            'timer'            : timer
        }

        minimizer.configure(**minimizer_options)
        minimizer.configure_nll(**nll_options)
        self.minimizer = minimizer
        self.default_nll_options = nll_options
        self.default_minimizer_options = minimizer_options
    
    def set_data(self, data_name:str='combData'):
        data = self.model.workspace.data(data_name)
        if not data:
            raise RuntimeError(f"workspace does not contain the dataset \"{data_name}\"")
        self.minimizer.set_data(data)
        self.model._data = data
        
    def set_blind_range(self, blind_range:List[float], categories:Optional[List[str]]=None):
        self.model.create_blind_range(blind_range, categories)
        sideband_range_name = self.model.get_sideband_range_name()
        self.minimizer.configure_nll(range=sideband_range_name, split_range=True, update=True)
        self._use_blind_range = True
        
    def unset_blind_range(self):
        self.minimizer.nll = None
        self.minimizer.nll_commands.pop("RangeWithName", None)
        self.minimizer.nll_commands.pop("SplitRange", None)
        self.stdout.info("INFO: Blind range removed from list of  NLL commands. NLL is reset.")
        self._use_blind_range = False
        
    def load_snapshot(self, snapshot_name:Optional[str]=None):
        if snapshot_name is not None:
            snapshot = self.model.workspace.getSnapshot(snapshot_name)
            if (not snapshot) and ('0x(nil)' in snapshot.__repr__()):
                self.stdout.warning(f"WARNING: Snapshot \"{snapshot_name}\" does not exist.")
            else:
                self.model.workspace.loadSnapshot(snapshot_name)
                self.stdout.debug(f"DEBUG: Loaded snapshot \"{snapshot_name}\"")
    
    def get_variables(self, variable_type:Union[str, WSVariables], sort:bool=True):
        return self.model.get_variables(variable_type, sort=sort)
    
    def save_snapshot(self, snapshot_name:Optional[str]=None, 
                      variables:Optional[Union[ROOT.RooArgSet, str, WSVariables]]=None):
        if snapshot_name is not None:
            if variables is None:
                self.model.workspace.saveSnapshot(snapshot_name, self.model.workspace.allVars())
            else:
                if isinstance(variables, (str, WSVariables)):
                    variables = self.get_variables(variables)
                self.model.workspace.saveSnapshot(snapshot_name, variables)
            self.stdout.debug(f"DEBUG: Saved snapshot \"{snapshot_name}\"")
        
    def save(self, fname:str, recreate:bool=True):
        self.model.save(fname, recreate=recreate)
        self.stdout.info(f"INFO: Saved workspace file as `{fname}`")