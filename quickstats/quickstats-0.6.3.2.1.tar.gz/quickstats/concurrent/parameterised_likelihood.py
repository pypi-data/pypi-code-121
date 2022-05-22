import os
import sys
import copy
import json
from typing import Optional, Union, Dict, List, Any
from itertools import repeat

import pandas as pd

import ROOT
from quickstats import semistaticmethod
from quickstats.parsers import ParamParser
from quickstats.concurrent import ParameterisedRunner
from quickstats.components import Likelihood
from quickstats.utils.common_utils import batch_makedirs
from quickstats.maths.numerics import pretty_value

class ParameterisedLikelihood(ParameterisedRunner):
    def __init__(self, input_file:str, param_expr:str,
                 filter_expr:Optional[str]=None, exclude_expr:Optional[str]=None,
                 data_name:str="combData", uncond_snapshot:Optional[str]=None,
                 config:Optional[Dict]=None, outdir:str="output",
                 outname:str="{poi_names}.json", cache:bool=True,
                 save_log:bool=True, parallel:int=-1,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(file_expr=None, param_expr=param_expr,
                         filter_expr=filter_expr, exclude_expr=exclude_expr,
                         parallel=parallel, timed=True, save_log=save_log,
                         cache=cache, allow_none=True, verbosity=verbosity)
        
        self.attributes = {
            'input_file': input_file,
            'data_name': data_name,
            'uncond_snapshot': uncond_snapshot,
            'config': config,
            'outdir': outdir,
            'outname': outname
        }
        
        self.attributes['poi_names'] = ParamParser._get_param_str_attributes(param_expr)

    def _prerun_batch(self):
        self.stdout.info("TIPS: When running likelihood scan on an Asimov dataset, remember to restore the global "
                         "observables to their Asimov values by loading the appropriate snapshot.")
        outdir = self.attributes['outdir']
        cache_dir = self.get_cache_dir()
        batch_makedirs([outdir, cache_dir])
    
    @semistaticmethod
    def _prerun_instance(self, filename:str, mode:int, poi_val:Optional[Union[float, Dict[str, float]]]=None, **kwargs):
        if mode == 2:
            param_str = "("+ParamParser.val_encode_parameters(poi_val)+")"
            self.stdout.info(f"INFO: Evaluating conditional NLL {param_str} for the workspace {filename}")
        elif mode == 1:
            self.stdout.info(f"INFO: Evaluating unconditional NLL for the workspace {filename}")
    
    @semistaticmethod
    def _cached_return(self, outname:str):
        with open(outname, 'r') as f:
            result = json.load(f)
            processed_result = self._process_result(result)
        return processed_result
    
    @semistaticmethod
    def _process_result(self, result:Dict):
        if 'uncond_fit' in result:
            fit_result = result['uncond_fit']
        elif 'cond_fit' in result:
            fit_result = result['cond_fit']
        else:
            raise RuntimeError("unexpected output (expect only conditional/unconditional fit in each task)")        
        nll   = fit_result['nll']
        mu    = fit_result.get("mu", {})
        muhat = fit_result.get("muhat", {})
        
        processed_result = {
            'nll': nll,
            'mu' : mu
        }
        processed_result['mu'].update(muhat)
        return processed_result
        
    @semistaticmethod
    def _run_instance(self, filename:str, mode:int,
                      poi_name:Optional[Union[str, List[str]]]=None,
                      poi_val:Optional[Union[float, Dict[str, float]]]=None,
                      data_name:str="combData",
                      snapshot_name:Optional[str]=None,
                      config:Optional[Dict]=None,
                      outname:Optional[str]=None,
                      **kwargs):
        try:
            if mode not in [1, 2, 4]:
                error_msg = "only unconditional/conditional fit is allowed in parameterised likelihood runner"
                self.stdout.error(error_msg)
                raise RuntimeError(error_msg)
            if config is None:
                config = {}
            verbosity = config.pop("verbosity", "INFO")
            do_minos = config.pop("do_minos", False)
            likelihood = Likelihood(filename=filename, poi_name=poi_name, data_name=data_name, 
                                    config=config, verbosity=verbosity)
            fit_result = likelihood.nll_fit(poi_val, mode=mode, do_minos=do_minos,
                                            snapshot_name=snapshot_name)
            # save results
            if outname is not None:
                with open(outname, 'w') as outfile:
                    json.dump(fit_result, outfile)
                print('INFO: Saved NLL result to {}'.format(outname))
            result = self._process_result(fit_result)
            return result
        except Exception as e:
            sys.stdout.write(f"{e}\n")
            return None
        
    def get_cache_dir(self):
        return os.path.join(self.attributes['outdir'], 'cache')
    
    def prepare_task_inputs(self):
        
        poi_names = self.attributes['poi_names']
        if len(poi_names) == 0:
            raise RuntimeError("no POI(s) to scan for")
            
        input_file = self.attributes['input_file']
        cache_dir  = self.get_cache_dir()
        outname    = "{param_str}.json"
        param_points = self.get_param_points(input_file)
        param_data = self.get_serialised_param_data(param_points, outdir=cache_dir, outname=outname)
        
        if self.attributes['uncond_snapshot'] is None:
            # None is for unconditional NLL
            poi_values = [None]
            # 1 is for unconditional NLL, 2 is for conditional NLL
            modes = [1] + [2]*len(param_points)
            snapshot_names = [Likelihood.kCurrentSnapshotName] * (1 + len(param_points))
        else:
            poi_values = [None]
            modes = [4] + [2]*len(param_points)
            uncond_snapshot_name = self.attributes['uncond_snapshot']
            snapshot_names = [uncond_snapshot_name] + [Likelihood.kCurrentSnapshotName] * len(param_points)
        
        for param_point in param_points:
            poi_values.append(param_point['internal_parameters'])
            
        outname_uncond = os.path.join(cache_dir, "{}_uncond.json".format("_".join(poi_names)))
        param_dpd_kwargs = {
            'poi_val': poi_values,
            'mode': modes,
            'snapshot_name': snapshot_names,
            'outname': [outname_uncond] + param_data['outnames']
        }
        
        filename = list(set(param_data['filenames']))
        
        if len(filename) == 0:
            raise RuntimeError(f"no input file found matching the expression: {input_file}")
        if len(filename) > 1:
            raise RuntimeError("multiple input files detected: {}".format(", ".join(filename)))
            
        param_ind_kwargs = {
            'filename': filename[0],
            'poi_name': self.attributes['poi_names'],
            'data_name': self.attributes['data_name'],
            'config': self.attributes['config']
        }
        
        self.set_param_ind_kwargs(**param_ind_kwargs)
        self.set_param_dpd_kwargs(**param_dpd_kwargs)
        kwarg_set = self.create_kwarg_set()
        auxiliary_args = {
            'points': poi_values
        }
        if not kwarg_set:
            raise RuntimeError("no parameter point to scan for")        
        return kwarg_set, auxiliary_args
    
    def postprocess(self, raw_result, auxiliary_args:Optional[Dict]=None):
        points = auxiliary_args['points']
        for result, poi_values in zip(raw_result, points):
            if result is None:
                if poi_values is None:
                    raise RuntimeError(f'NLL evaluation failed for the unconditional fit. '
                                       'Please check the log file for more details.')
                else:
                    param_str = ParamParser.val_encode_parameters(poi_values)
                    raise RuntimeError(f'NLL evaluation failed for the conditional fit ({param_str}).'
                                       'Please check the log file for more details.')
            if not isinstance(result, dict):
                raise RuntimeError("found cache result with deprecated format, a rerun "
                                   "is needed")
        uncond_result = raw_result[0]
        uncond_nll = uncond_result['nll']
        data = {'nll':[], 'qmu':[]}
        poi_names = self.attributes['poi_names']
        for poi_name in poi_names:
            data[poi_name] = []
        for result, poi_values in zip(raw_result, points):
            nll   = result['nll']
            data['nll'].append(nll)
            data['qmu'].append(2*(nll-uncond_nll))
            for poi_name in poi_names:
                mu_map = result['mu']
                if poi_name not in mu_map:
                    if poi_values is None:
                        raise RuntimeError(f'unable to extract value for the POI "{poi_name}" '
                                           f'for the unconditional fit. Please check the log '
                                           f'file for more details')
                    else:
                        param_str = ParamParser.val_encode_parameters(poi_values)
                        raise RuntimeError(f'unable to extract value for the POI "{poi_name}" '
                                           f'for the conditional fit ({param_str}). Please check the log '
                                           f'file for more details')
                mu = mu_map[poi_name]
                data[poi_name].append(mu)
        # backward compatibility
        if len(poi_names) == 1:
            poi_name = poi_names[0]
            data['mu'] = [v for v in data[poi_name]]
        outdir  = self.attributes['outdir']
        outname = self.attributes['outname'].format(poi_names="_".join(poi_names))
        outpath = os.path.join(outdir, outname.format(poi_name=poi_name))
        with open(outpath, 'w') as outfile:
            json.dump(data, outfile, indent=3)