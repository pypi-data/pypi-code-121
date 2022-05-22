import os
import copy
import math
import time
import json
from itertools import repeat
from typing import Optional, Dict, List, Union

import numpy as np
import ROOT
from quickstats.components import ExtendedModel, ExtendedMinimizer
from quickstats.maths.numerics import approx_n_digit, str_encode_value, str_decode_value, pretty_value
from quickstats.utils import common_utils

def load_cache(fname:str):
    if (fname is not None) and os.path.exists(fname):
        with open(fname, 'r') as file:
            data = json.load(file)
        return data
    else:
        return None

from quickstats.components import AnalysisObject
from quickstats.utils.common_utils import parse_config

class Likelihood(AnalysisObject):
    
    def __init__(self, filename:str, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:str='combData', 
                 config:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        config = parse_config(config)
        config['filename']  = filename
        config['poi_name']  = poi_name
        config['data_name'] = data_name
        config['verbosity'] = verbosity
        self._inherit_init(super().__init__, **config)
        self.roofit_result = None
    
    @staticmethod
    def _parse_poi_val(pois:"ROOT.RooArgSet", poi_val:Optional[Union[Dict[str, float], float]]=None):
        if poi_val is None:
            poi_val = {}
            for poi in pois:
                poi_val[poi.GetName()] = poi.getVal()
        elif not isinstance(poi_val, dict):
            poi_val_tmp = poi_val
            poi_val = {}
            for poi in pois:
                poi_val[poi.GetName()] = poi_val_tmp
        else:
            # fill in missing values
            for poi in pois:
                poi_name = poi.GetName()
                if poi_name not in poi_val:
                    poi_val[poi_name] = poi.getVal()
        return poi_val
        
    def nll_fit(self, poi_val:Optional[Union[Dict[str, float], float]]=None,
                mode:int=2, snapshot_name:Optional[str]=AnalysisObject.kCurrentSnapshotName,
                do_minos:bool=False):
        if not isinstance(self.poi, ROOT.RooArgSet):
            pois = ROOT.RooArgSet(self.poi)
        else:
            pois = self.poi
        
        poi_val = self._parse_poi_val(pois, poi_val)

        if snapshot_name is None:
            self.save_snapshot(self.kTempSnapshotName)
            snapshot_name = self.kTempSnapshotName
        
        nll_uncond = None
        nll_cond   = None
        muhat      = None
        
        tmp_do_minos = self.minimizer.config['minos']
        
        self.minimizer.config['minos'] = do_minos
        if do_minos:
            self.minimizer.minos_set = pois
        
        start_time = time.time()
        roofit_result = {}
        muhat = {}
        muhat_errlo = {}
        muhat_errhi = {}
        
        # no poi fit
        if mode == 3:
            # restore initial parameter values after each fit
            self.load_snapshot(snapshot_name)
            self.minimizer.create_nll()
            prefit_nll = self.minimizer.nll.getVal()
            fit_status = self.minimizer.minimize()
            roofit_result = self.minimizer.fit_result
            self.save_snapshot("nllFit")
            postfit_nll = self.minimizer.nll.getVal()
            fit_time = time.time() - start_time
            
        # unconditional nll
        if mode in [0, 1, 4]:
            # restore initial parameter values after each fit
            self.load_snapshot(snapshot_name)
            # fix other pois if they are not studied
            for poi in self.model.pois:
                poi.setConstant(1)
            for poi in pois:
                poi.setConstant(0)
                val = poi_val[poi.GetName()]
                if val is not None:
                    poi.setVal(val)
            if mode == 4:
                self.minimizer.create_nll()
                fit_status_uncond = None
                roofit_result['uncond'] = None
            else:
                fit_status_uncond = self.minimizer.minimize()
                roofit_result['uncond'] = self.minimizer.fit_result
            self.save_snapshot("uncondFit")
            nll_uncond = self.minimizer.nll.getVal()
            for poi in pois:
                poi_name = poi.GetName()
                muhat[poi_name]       = poi.getVal()
                muhat_errlo[poi_name] = poi.getErrorLo()
                muhat_errhi[poi_name] = poi.getErrorHi()
        fit_time_uncond = time.time() - start_time
        # conditional nll
        if mode in [0, 2]:
            # restore initial parameter values after each fit
            self.load_snapshot(snapshot_name)
            # fix other pois if they are not studied
            for poi in self.model.pois:
                poi.setConstant(1)
            for poi in pois:
                val = poi_val.get(poi.GetName(), poi.getVal())
                # profiled poi
                if val is None:
                    poi.setConstant(0)
                else:
                    poi.setConstant(1)
                    poi.setVal(val)
            fit_status_cond = self.minimizer.minimize()
            roofit_result['cond'] = self.minimizer.fit_result
            self.save_snapshot("condFit")
            nll_cond = self.minimizer.nll.getVal()
        fit_time_cond = time.time() - fit_time_uncond - start_time
        
        fit_result = {}
        self.stdout.info("INFO: NLL evaluation completed with")
        if mode in [0, 1, 4]:
            best_fit_str = ", ".join([f"{name}={value:.5f}" for name, value in muhat.items()])
            self.stdout.info("best fit : ".rjust(15) + f"{best_fit_str}")
            self.stdout.info("uncond NLL = ".rjust(15) + f"{nll_uncond:.5f}")
            fit_result['uncond_fit'] = {
                'muhat': muhat,
                'muhat_errlo': muhat_errlo,
                'muhat_errhi': muhat_errhi,
                'nll': nll_uncond,
                'status': fit_status_uncond,
                'time': fit_time_uncond
            }
        if mode in [0, 2]:
            mu = {name:pretty_value(value) for name, value in poi_val.items()}
            mu_str = ", ".join([f"{name}={pretty_value(value)}" for name, value in poi_val.items()])
            self.stdout.info("mu : ".rjust(15) + f"{mu_str}")
            # also add the best-fit value for profiled POIs
            for name, value in poi_val.items():
                if value == None:
                    muhat[name] = self.model.workspace.var(name).getVal()
            self.stdout.info("cond NLL = ".rjust(15)+f"{nll_cond:.5f}")
            fit_result['cond_fit'] = {
                'mu': mu,
                'muhat': muhat,
                'nll': nll_cond,
                'status': fit_status_cond,
                'time': fit_time_cond
            }
            
        if mode == 0:
            pnll = nll_cond - nll_uncond
            qmu  = 2*pnll
            self.stdout.info("PNLL = ".rjust(15) + "{:.5f}".format(nll_cond - nll_uncond))
            fit_result['pnll'] = pnll
            fit_result['qmu']  = qmu
            
            if (qmu >= 0):
                ndof = len(pois)
                if ndof == 1:
                    # ndof = 1 case
                    poi_name = pois.first().GetName()
                    x0 = poi_val[poi_name]
                    significance = math.sqrt(qmu)
                    pvalue = 1 - ROOT.Math.normal_cdf(significance, 1, x0)
                else:
                    x0 = list(set(poi_val.values()))
                    if len(x0) > 1:
                        fit_result['significance'] = None
                        fit_result['pvalue'] = None
                    else:
                        pvalue = ROOT.Math.chisquared_cdf_c(qmu, ndof, x0[0])
                        significance = ROOT.RooStats.PValueToSignificance(pvalue)
                fit_result['significance'] = significance
                fit_result['pvalue'] = pvalue
            else:
                fit_result['significance'] = None
                fit_result['pvalue'] = None
                
        if mode != 3:
            self.stdout.info("time = ".rjust(15) + \
                             "(uncond_fit) {:.3f}, (cond_fit) {:.3f}".format(fit_time_uncond, fit_time_cond))
            fit_result['total_time'] = fit_time_uncond + fit_time_cond
        else:
            self.stdout.info("prefit NLL = ".rjust(18) + f"{prefit_nll:.5f}")
            self.stdout.info("postfit NLL = ".rjust(18) + f"{postfit_nll:.5f}")
            self.stdout.info("time = ".rjust(18) + f"{fit_time:.3f}")
            fit_result['prefit_nll'] = prefit_nll
            fit_result['postfit_nll'] = postfit_nll
            fit_result['total_time'] = fit_time
        
        self.roofit_result = roofit_result
        
        # finallizing
        self.minimizer.config['minos'] = tmp_do_minos
        self.minimizer.minos_set = ROOT.RooArgSet()
        
        return fit_result
        
    def evaluate_nll(self, poi_val:Optional[Union[Dict[str, float], float]]=None,
                     mode:int=2, snapshot_name:Optional[str]="currentSnapshot"):
        """Evalute post-fit NLL value
        
        Arguments:
            poi_val: (Optional) float
                Value of parameter of interest during fit. If not specified, the original value is used.
            mode: int
                Evaluation mode. Choose from:
                    0: Evaluate nll_mu - nll_muhat
                    1: Evaluate unconditional NLL (nll_muhat)
                    2: Evaluate conditional NLL (nll_mu)
                    3: Evaluate post-fit NLL (POI state remain as is)
            snapshot_name: (Optional) str
                Name of snapshot to load before fitting.
        """
        fit_result = self.nll_fit(poi_val=poi_val, mode=mode, snapshot_name=snapshot_name)
        
        if mode == 0:
            return fit_result['pnll']
        if mode == 1:
            return fit_result['uncond_fit']['nll']
        if mode == 2:
            return fit_result['cond_fit']['nll']
        if mode == 3:
            return fit_result['postfit_nll']