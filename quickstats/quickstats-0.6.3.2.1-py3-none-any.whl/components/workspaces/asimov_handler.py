from typing import Optional, Union, List, Dict

import ROOT

from quickstats.components import AnalysisBase
from quickstats.maths.numerics import is_float
from quickstats.utils.common_utils import format_delimiter_enclosed_text

class AsimovHandler(AnalysisBase):
    _DEFAULTS_ = {
        "raw": "raw",
        "fit": "fit",
        "reset": "reset",
        "gen_asimov": "genasimov",
        "float": "float",
        "fix_syst": "fixsyst",
        "fix_all": "fixall",
        "match_glob": "matchglob",
        "save_snapshot": "savesnapshot"
    }
    def __init__(self, ws:ROOT.RooWorkspace, data_name:str,
                 range_name:Optional[str]=None,
                 minimizer_config:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(ws, poi_name=[], data_name=data_name,
                         config=minimizer_config, verbosity=verbosity)
        self.range_name = range_name
        self.initialize()

    def initialize(self):
        self.core_variables = self.get_variables("core")
        self.save_snapshot(self._DEFAULTS_['raw'], self.core_variables)
        self.saved_snapshots = [self._DEFAULTS_['raw']]
        
    def parse_setup(self, setup_str:str):
        setup_str = setup_str.replace(" ", "")
        fix_setup = []
        profile_setup = []
        invalid_setup = []
        undefined_setup = []
        tokens = setup_str.split(",")
        for token in tokens:
            subtokens = token.split("=")
            if len(subtokens) != 2:
                invalid_setup.append(token)
                continue
            name = subtokens[0]
            expr = subtokens[1]
            if not self.model.workspace.var(name):
                undefined_setup.append(name)
                continue
            expr_tokens = expr.split("_")
            if len(expr_tokens) not in [1, 3]:
                invalid_setup.append(token)
                continue
            if len(expr_tokens) == 1:
                if not is_float(expr_tokens[0]):
                    invalid_setup.append(token)
                    continue
                else:
                    fix_setup.append(token)
            elif len(expr_tokens) == 3:
                if not all(is_float(t) for t in expr_tokens):
                    invalid_setup.append(token)
                    continue
                else:
                    profile_setup.append(token)
        passed = (len(invalid_setup) == 0) and (len(undefined_setup) == 0)
        if len(invalid_setup) > 0:
            invalid_setup_str = ", ".join([f"`{s}`" for s in invalid_setup])
            self.stdout.error(f"ERROR: Invalid setup info {invalid_setup_str}.", "red")
        if len(undefined_setup) > 0:
            undefined_setup_str = ", ".join([f"`{s}`" for s in undefined_setup])
            self.stdout.error(f"ERROR: Setup info with undefined variable {undefined_setup_str}.", "red")
        if passed:
            if (not fix_setup) and (not profile_setup):
                self.stdout.info("REGTEST: There is no setup info provided. "
                                 "Proceed with current variable values and ranges.")
            setups = {
                "fix_param"    : ",".join(fix_setup),
                "profile_param": ",".join(profile_setup)
            }
            return setups
        return None
    
    def translate_xml_attributes(self, attributes:Dict):
        result = {
            'name': attributes['Name'],
            'setup': attributes.get("Setup", ""),
            'action': attributes.get("Action", ""),
            'snapshot_all': attributes.get("SnapshotAll", ""),
            'snapshot_glob': attributes.get("SnapshotGlob", ""),
            'snapshot_nuis': attributes.get("SnapshotNuis", ""),
            'snapshot_poi': attributes.get("SnapshotPOI", ""),
            'data': attributes.get("Data", ""),
            'algorithm': attributes.get("Algorithm", "roostats")
        }
        return result
    
    def profile_to_data(self, data_name:str=""):
        tmp_data = self.model.data
        switch_data = (data_name != "") and (data_name != self.model.data.GetName())
        if switch_data:
            new_data = self.model.workspace.data(data_name)
            if not new_data:
                raise RuntimeError(f"dataset `{new_data}` not found in the workspace")
            self.set_data(new_data)
        # use range name when fitting to observed data
        if self.range_name and (not switch_data):
            self.set_range_name(self.range_name)
        fit_status = self.minimizer.minimize()
        # restore default dataset
        if switch_data:
            self.set_data(tmp_data)
        self.unset_range_name()
        return fit_status
    
    def set_range_name(self, range_name:str):
        self.minimizer.configure_nll(range=range_name, split_range=True, update=True)
        
    def unset_range_name(self):
        self.minimizer.nll = None
        self.minimizer.nll_commands.pop("RangeWithName", None)
        self.minimizer.nll_commands.pop("SplitRange", None)
    
    def generate_single_asimov(self, attributes:Dict):
        orig_snapshot = self.core_variables.snapshot()
        config = self.translate_xml_attributes(attributes)
        asimov_name = config['name']
        title_str = format_delimiter_enclosed_text(f"Operation {asimov_name}", "+")
        self.stdout.info(title_str)
        setup_str = config['setup'].strip()
        if setup_str:
            setup_kwargs = self.parse_setup(setup_str)
            if not setup_kwargs:
                self.stdout.error(f"\tStop generating Asimov data `{asimov_name}`")
                return None
            else:
                self.setup_parameters(**setup_kwargs, update_snapshot=False)
        action_str = config['action'].strip()
        self.stdout.info(f"REGTEST: Action list ({action_str})")
        if not action_str:
            return None
        action_list = action_str.split(":")
        fixed_variables = []
        for action in action_list:
            status = -1
            if action == self._DEFAULTS_['fit']:
                data_name = config['data']
                status = self.profile_to_data(data_name)
                if status not in [0, 1]:
                    raise RuntimeError("fit not converging properly")
            # reset to initial parameter values
            elif action == self._DEFAULTS_['raw']:
                self.load_snapshot(self._DEFAULTS_['raw'])
            # reset to parameter values at beginning of this round
            elif action == self._DEFAULTS_['reset']:
                self.core_variables.__assign__(orig_snapshot)
            # float fixed nuisance parameters
            elif action == self._DEFAULTS_['float']:
                for varname in fixed_variables:
                    if self.model.pois.find(varname):
                        continue
                    else:
                        self.model.workspace.var(varname).setConstant(False)
            elif action == self._DEFAULTS_['gen_asimov']:
                self.stdout.info(f"REGTEST: Generating Asimov dataset `{asimov_name}`")
                algorithm = config['algorithm']
                if algorithm == "roostats":
                    generator = ROOT.RooStats.AsymptoticCalculator.GenerateAsimovData
                    asimov_data = generator(self.model.pdf, self.model.observables)
                    getattr(self.model.workspace, "import")(asimov_data, ROOT.RooFit.Rename(asimov_name))
                else:
                    asimov_data = self.model.generate_asimov(do_fit=False, modify_globs=False, do_import=True,
                                                             asimov_name=asimov_name, restore_status=0)
            elif action == self._DEFAULTS_['fix_syst']:
                constrained_np = self.model.get_constrained_nuisance_parameters()
                for np in constrained_np:
                    np.setConstant(True)
                fixed_variables += [np.GetName() for np in constrained_np]
            elif action == self._DEFAULTS_['fix_all']:
                all_np = self.model.nuisance_parameters
                for np in all_np:
                    np.setConstant(True)
                fixed_variables += [np.GetName() for np in all_np]
            elif action == self._DEFAULTS_['match_glob']:
                if len(self.model.global_observables) > 0:
                    self.model.match_globs()
            elif action == self._DEFAULTS_['save_snapshot']:
                param_str_map = {
                    'all': 'parameters of interest, nuisance parameters, and global observables',
                    'nuis': 'nuisance parameters',
                    'glob': 'global observables',
                    'poi': 'parameters of interest'
                }
                param_var_map = {
                    'all': self.core_variables,
                    'nuis': self.model.nuisance_parameters,
                    'glob': self.model.global_observables,
                    'poi': self.model.pois,
                }                
                for param, param_str in param_str_map.items():
                    snapshot_name = config[f"snapshot_{param}"]
                    if snapshot_name != "":
                        self.stdout.info(f"REGTEST: Saving snapshot {snapshot_name} for current {param_str}")
                        self.save_snapshot(snapshot_name, param_var_map[param])
                        self.saved_snapshots.append(snapshot_name)
            elif action in self.saved_snapshots:
                self.load_snapshot(action)
            else:
                raise RuntimeError(f"unknown action {action}")