from typing import List, Optional, Union, Dict, Callable, Tuple
from itertools import repeat
import os
import sys
import copy
import json
import time
import uuid

import numpy as np

import ROOT

import quickstats
from quickstats import semistaticmethod, cls_method_timer
from quickstats.components import AbstractObject
from quickstats.utils.root_utils import load_macro, is_corrupt
from quickstats.utils.common_utils import combine_dict, execute_multi_tasks

class SignalModelling(AbstractObject):
    
    _DEFAULT_FIT_OPTION_ = {
        'print_level': -1,
        'min_fit': 2,
        'max_fit': 3,
        'binned': False,
        'range_expand_rate': 1,
        'minos': False,
        'hesse': True,
        'sumw2': True
    }
    
    _DEFAULT_PLOT_OPTION_ = {
        'bin_range': None,
        'n_bins_data': None,
        'n_bins_pdf': 1000,
        'plot_comparison': True,
        'comparison_mode': 'difference',
        'show_params': True,
        'show_stats': True,
        'styles': None,
        "xlabel": None,
        "ylabel": "Events / ({bin_width:.2f})",
        "annotations": None
    }

    _EXTERNAL_PDF_ = ['RooTwoSidedCBShape']
    
    _PDF_MAP_ = {
        'DSCB': 'RooTwoSidedCBShape',
        'ExpGaussExp': 'RooExpGaussExpShape',
        'Exp': 'RooExponential',
        'Bukin': 'RooBukinPdf'
    }
    
    @property
    def plot_options(self):
        return self._plot_options
    
    @property
    def fit_options(self):
        return self._fit_options
    
    @property
    def model_class(self):
        return self._model_class
    
    @property
    def param_templates(self):
        return self._param_templates

    def __init__(self, observable:str, fit_range:Union[List[float], Tuple[float]],
                 functional_form:Union[str, Callable],
                 param_templates:Optional[Callable]=None,
                 weight:str="weight", n_bins:Optional[int]=None,
                 fit_options:Optional[Dict]=None, plot_options:Optional[Dict]=None,
                 verbosity:str="INFO"):
        super().__init__(verbosity=verbosity)
        _fit_options = {
            'observable': observable,
            'functional_form': functional_form,
            'weight': weight,
            'range': fit_range,
            'n_bins': n_bins
        }
        self._fit_options = combine_dict(self._DEFAULT_FIT_OPTION_)
        self._plot_options = combine_dict(self._DEFAULT_PLOT_OPTION_, plot_options)
        self.update_fit_options(_fit_options)
        self.update_fit_options(fit_options)
        self._param_templates = param_templates
        self._model_class = None
        self.initialize()
        
    def initialize(self):
        ROOT.gROOT.SetBatch(True)
        self.configure_default_fit_options(self.fit_options['print_level'])
        ROOT.TH1.SetDefaultSumw2(True)
        functional_form = self.fit_options['functional_form']
        self._model_class = self.get_model_class(functional_form)
        if self.param_templates is None:
            if isinstance(functional_form, str):
                self._param_templates = self.get_param_templates(functional_form)
            else:
                raise RuntimeError("missing parameter templates definition")        
        
    def update_fit_options(self, options:Optional[Dict]=None):
        self._fit_options = combine_dict(self._fit_options, options)
        
    def update_plot_options(self, options:Optional[Dict]=None):
        self._plot_options = combine_dict(self._plot_options, options)        
        
    def set_param_templates(self, param_templates:Callable):
        self._param_templates = param_templates
        
    @semistaticmethod
    def load_extension(self, name:str):
        result = load_macro(name)
        if (result is not None) and hasattr(ROOT, name):
            self.stdout.info(f'INFO: Loaded extension module "{name}"')
                
    @semistaticmethod
    def get_model_class(self, name:Union[str, Callable]):
        if isinstance(name, Callable):
            return name
        pdf_name = self._PDF_MAP_.get(name, name)
        if not hasattr(ROOT, pdf_name):
            if pdf_name in self._EXTERNAL_PDF_:
                self.load_extension(pdf_name)
            else:
                raise ValueError(f"{name} is not a valid pdf name defined by ROOT")
        if not hasattr(ROOT, pdf_name):
            raise RuntimeError(f"failed to load pdf {pdf_name}")
        pdf = getattr(ROOT, pdf_name)
        return pdf
    
    @semistaticmethod
    def get_param_templates(self, name:Union[str, Callable]):
        if isinstance(name, Callable):
            return name
        from quickstats.components.model_param_templates import get_param_templates
        return get_param_templates(name)
    
    @staticmethod
    def configure_default_fit_options(print_level:int=-1):
        ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(print_level)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.NumIntegration)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Fitting)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Minimization)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.InputArguments)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Eval)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

    def sanity_check(self):
        if self.model_class is None:
            raise RuntimeError("model pdf not set")
        if self.param_templates is None:
            raise RuntimeError("model parameter templates not set")
        
    @staticmethod
    def create_obs_and_weight(obs_name:str, obs_range:List[float], 
                              weight_name:Optional[str]=None,
                              n_bins:Optional[int]=None):
        
        observable = ROOT.RooRealVar(obs_name, obs_name, obs_range[0], obs_range[1])
        
        # for chi-square calculation and plotting
        if n_bins is not None:
            observable.setBins(n_bins)
            
        if weight_name is not None:
            weight = ROOT.RooRealVar(weight_name, weight_name, -1000, 1000)
        else:
            weight = None

        return observable, weight
    
    @staticmethod
    def create_model_parameters(param_templates:Callable,
                                observable:"ROOT.RooRealVar",
                                weight:Optional["ROOT.RooRealVar"]=None,
                                tree:Optional["ROOT.TTree"]=None,
                                hist:Optional["ROOT.TH1"]=None,
                                n_bins:Optional[int]=None):
        if weight is not None:
            weight = weight.GetName()
        model_parameters = param_templates(observable, weight=weight,
                                           n_bins=n_bins, tree=tree,
                                           hist=hist)
        return model_parameters
    
    @staticmethod
    def create_dataset(tree:"ROOT.TTree", observable:"ROOT.RooRealVar",
                       weight:Optional["ROOT.RooRealVar"]=None):
        obs_name = observable.GetName()
        dataset_name = f"dataset_{obs_name}"
        if weight is None:
            dataset = ROOT.RooDataSet(dataset_name, dataset_name, tree,
                                      ROOT.RooArgSet(observable))
        else:
            weight_name = weight.GetName()
            dataset = ROOT.RooDataSet(dataset_name, dataset_name, tree,
                                      ROOT.RooArgSet(observable, weight),
                                      "", weight_name)
        return dataset
    
    @staticmethod
    def is_fit_success(fit_result:"ROOT.RooFitResult"):
        status   = fit_result.status()
        cov_qual = fit_result.covQual()
        return (status == 0) and (cov_qual in [-1, 3])
    
    @semistaticmethod
    def fit_model(self, model:"ROOT.RooAbsPdf", data:"ROOT.RooAbsData", observable:"ROOT.RooRealVar",
                  minos:bool=False, hesse:bool=True, sumw2:bool=True, min_fit:int=2, max_fit:int=3,
                  range_expand_rate:int=1, print_level:int=-1):
        vmin = observable.getMin()
        vmax = observable.getMax()
        observable.setRange("fitRange", vmin, vmax)
        
        model_name = model.GetName()
        data_name = data.GetName()
        obs_name = observable.GetName()
        
        self.stdout.info(f"INFO: Begin model fitting...")
        self.stdout.info(f"      Model : ".rjust(20) + f"{model_name}")
        self.stdout.info(f"    Dataset : ".rjust(20) + f"{data_name}")
        self.stdout.info(f" Observable : ".rjust(20) + f"{obs_name}")
        
        fit_args = [ROOT.RooFit.Range("fitRange"), ROOT.RooFit.PrintLevel(print_level),
                    ROOT.RooFit.Minos(minos), ROOT.RooFit.Hesse(hesse),
                    ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(sumw2)]

        status_label = {
            True: 'SUCCESS',
            False: 'FAIL'
        }

        for i in range(1, max_fit + 1):
            fit_result = model.fitTo(data, *fit_args)           
            is_success = self.is_fit_success(fit_result)
            self.stdout.info(f" Fit iteration {i} : ".rjust(20) + f"{status_label[is_success]}")
            if i >= min_fit:
                if is_success:
                    return fit_result
                else:
                    new_vmin = observable.getRange("fitRange").first - range_expand_rate
                    new_vmax = observable.getRange("fitRange").second + range_expand_rate
                    self.stdout.info(f"INFO: Fit failed to converge, refitting with "
                                     f"expanded fit range [{new_vmin}, {new_vmax}]")
                    observable.setRange("fitRange", new_vmin, new_vmax)
        return fit_result
    
    @staticmethod
    def _set_pdf_param_values(pdf:ROOT.RooAbsPdf, observable:ROOT.RooRealVar, param_values:Dict):
        params = pdf.getParameters(observable)
        for param in params:
            param_name = param.GetName()
            if param_name not in param_values:
                raise RuntimeError(f"missing value for the parameter: {param_name}")
            param_value = param_values[param_name]
            param.setVal(param_value)
    
    @staticmethod
    def export_hist_data(data:ROOT.RooDataSet, pdf:ROOT.RooAbsPdf, observable:ROOT.RooRealVar,
                         bin_range:Optional[List]=None, n_bins_data:Optional[int]=None,
                         n_bins_pdf:Optional[int]=1000, bin_error:bool=False):
        if bin_range is None:
            bin_range = observable.getRange()
            bin_range = [bin_range.first, bin_range.second]
            
        if n_bins_data is None:
            n_bins_data = observable.getBins()
        
        if n_bins_pdf is None:
            n_bins_pdf = n_bins_data
        binning_data = ROOT.RooFit.Binning(n_bins_data, bin_range[0], bin_range[1])
        binning_pdf = ROOT.RooFit.Binning(n_bins_pdf, bin_range[0], bin_range[1])
        from quickstats.interface.root import RooAbsData
        h_data = RooAbsData.create_histogram(data, uuid.uuid4().hex, observable, binning_data)
        h_pdf = RooAbsData.create_histogram(pdf, uuid.uuid4().hex, observable, binning_pdf)
        h_pdf_data_binning = RooAbsData.create_histogram(pdf, uuid.uuid4().hex, observable,
                                                         binning_data)
        from quickstats.interface.root import TH1
        if bin_error:
            bin_errors = TH1.GetPoissonError(h_data.bin_content)
        else:
            size = len(h_data.bin_content)
            bin_errors = {"lo": np.zeros(size), "hi": np.zeros(size)}
        norm_data  = h_data.bin_content.sum()
        norm_pdf1  = h_pdf.bin_content.sum()
        norm_pdf2  = h_pdf_data_binning.bin_content.sum()
        hist_data = {
            'data': {
                'x': h_data.bin_center,
                'y': h_data.bin_content,
                'yerrlo': bin_errors['lo'],
                'yerrhi': bin_errors['hi']
            },
            'pdf': {
                'x': h_pdf.bin_center,
                'y': h_pdf.bin_content * norm_data / norm_pdf1 * (n_bins_pdf / n_bins_data)
            },
            'pdf_data_binning': {
                'x': h_pdf_data_binning.bin_center,
                'y': h_pdf_data_binning.bin_content * norm_data / norm_pdf2
            }
        }
        return hist_data    
    
    @staticmethod
    def get_fit_stats(model:"ROOT.RooAbsPdf", data:"ROOT.RooAbsData", observable:"ROOT.RooRealVar",
                      n_float_params:int=0):
        n_bins = observable.numBins()
        # +1 is there to account for the normalization that is done internally in RootFit
        ndf = n_bins - (n_float_params + 1)
        frame = observable.frame()
        data.plotOn(frame)
        model.plotOn(frame)
        chi2_reduced = frame.chiSquare(n_float_params)
        chi2 = chi2_reduced * ndf
        pvalue = ROOT.TMath.Prob(chi2, ndf)
        fit_stats = {
            'n_bins': n_bins,
            'n_float_params': n_float_params,
            'ndf': ndf,
            'chi2/ndf': chi2_reduced,
            'chi2': chi2,
            'pvalue': pvalue
        }
        return fit_stats
        
    @staticmethod
    def get_param_summary(variables:List["ROOT.RooRealVar"]):
        param_summary = {}
        for name in variables:
            param_summary[name] = {
                'value': variables[name].getVal(),
                'errorhi': variables[name].getErrorHi(),
                'errorlo': variables[name].getErrorLo()
            }
        return param_summary

    def _run(self, fname:str, tree_name:str, model_class:Callable, param_templates:Callable,
             fit_options:Dict, plot_options:Optional[Dict]=None, save_summary_as:Optional[str]=None, 
             save_param_as:Optional[str]=None, save_plot_as:Optional[str]=None):
        t1 = time.time()
        c = ROOT.TCanvas(uuid.uuid4().hex)
        f = ROOT.TFile(fname)
        if is_corrupt(f):
            raise RuntimeError(f"file \"{fname}\" is corrupted")
        tree = f.Get(tree_name)
        if not tree:
            raise RuntimeError(f"failed to load tree \"{tree_name}\"")
        obs_name  = fit_options['observable']
        obs_range = fit_options['range']
        weight    = fit_options['weight']
        n_bins    = fit_options['n_bins']
        observable, weight = self.create_obs_and_weight(obs_name, obs_range, weight, n_bins)
        model_parameters = self.create_model_parameters(param_templates, observable=observable,
                                                        weight=weight, tree=tree, n_bins=n_bins)
        data = self.create_dataset(tree, observable, weight)
        model_name = f"model_{model_class.Class_Name()}"
        model_pdf = model_class(model_name, model_name, observable, *model_parameters.values())
        kwargs = {
            'minos': fit_options['minos'],
            'hesse': fit_options['hesse'],
            'sumw2': fit_options['sumw2'],
            'min_fit': fit_options['min_fit'],
            'max_fit': fit_options['max_fit'],
            'range_expand_rate': fit_options['range_expand_rate'],
            'print_level': fit_options['print_level']
        }
        
        fit_result = self.fit_model(model_pdf, data, observable, **kwargs)
        fit_result.Print()
        
        n_float_params = fit_result.floatParsFinal().getSize()
        fit_stats = self.get_fit_stats(model_pdf, data, observable, n_float_params=n_float_params)
        
        self.stdout.info(f"INFO: chi^2/ndf = {fit_stats['chi2/ndf']}, "
                         f"Number of Floating Parameters + Normalization = {fit_stats['n_float_params'] + 1}, "
                         f"Number of bins = {fit_stats['n_bins']}, "
                         f"ndf = {fit_stats['ndf']}, "
                         f"chi^2 = {fit_stats['chi2']}, "
                         f"p_value = {fit_stats['pvalue']}")
        param_summary = self.get_param_summary(model_parameters)
        t2 = time.time()
        time_taken = t2 - t1
        self.stdout.info(f"INFO: Task finished. Total time taken: {time_taken:.4f}s")
        summary = {"fname": fname,
                   "parameters": param_summary,
                   "stats": fit_stats,
                   "fit_options": copy.deepcopy(fit_options),
                   "time": time_taken}
        if not isinstance(summary['fit_options']['functional_form'], str):
            summary['fit_options']['functional_form'] = type(summary['fit_options']['functional_form']).__name__
            
        param_data = self._get_simplified_param_data(param_summary)
            
        if save_plot_as is not None:
            if plot_options is None:
                plot_options = combine_dict(self._DEFAULT_PLOT_OPTION_)
            hist_data = self.export_hist_data(data, model_pdf, observable, 
                                              bin_range=plot_options['bin_range'],
                                              n_bins_data=plot_options['n_bins_data'],
                                              n_bins_pdf=plot_options['n_bins_pdf'])
            kwargs = {
                "xlabel": plot_options['xlabel'],
                "ylabel": plot_options['ylabel'],
                "plot_comparison" : plot_options['plot_comparison'],
                "comparison_mode" : plot_options['comparison_mode'],
                "styles" : plot_options['styles'],
                "annotations": plot_options['annotations']
            }
            if plot_options['show_params']:
                kwargs["param_data"] = param_data
            if plot_options["show_stats"]:
                kwargs["stat_data"] = {"chi2/ndf": summary["stats"]["chi2/ndf"]}
            self.create_plot(hist_data, outname=save_plot_as, **kwargs)
        # free memory
        c.Close()
        ROOT.gSystem.ProcessEvents()
 
        if save_param_as is not None:
            with open(save_param_as, "w") as out:
                json.dump(param_data, out, indent=2)
        if save_summary_as is not None:
            with open(save_summary_as, "w") as out:
                json.dump(summary, out, indent=2)

        return summary
    
    @staticmethod
    def _get_simplified_param_data(param_data:Dict):
        simplified_param_data = {}
        for param in param_data:
            simplified_param_data[param] = param_data[param]['value']
        return simplified_param_data
       
    @staticmethod
    def export_hist_data(data:ROOT.RooDataSet, pdf:ROOT.RooAbsPdf, observable:ROOT.RooRealVar,
                         bin_range:Optional[List]=None, n_bins_data:Optional[int]=None,
                         n_bins_pdf:Optional[int]=1000, bin_error:bool=False):
        if bin_range is None:
            bin_range = observable.getRange()
            bin_range = [bin_range.first, bin_range.second]
            
        if n_bins_data is None:
            n_bins_data = observable.getBins()
        
        if n_bins_pdf is None:
            n_bins_pdf = n_bins_data
        binning_data = ROOT.RooFit.Binning(n_bins_data, bin_range[0], bin_range[1])
        binning_pdf = ROOT.RooFit.Binning(n_bins_pdf, bin_range[0], bin_range[1])
        from quickstats.interface.root import RooAbsData
        h_data = RooAbsData.create_histogram(data, uuid.uuid4().hex, observable, binning_data)
        h_pdf = RooAbsData.create_histogram(pdf, uuid.uuid4().hex, observable, binning_pdf)
        h_pdf_data_binning = RooAbsData.create_histogram(pdf, uuid.uuid4().hex, observable,
                                                         binning_data)
        from quickstats.interface.root import TH1
        if bin_error:
            bin_errors = TH1.GetPoissonError(h_data.bin_content)
        else:
            size = len(h_data.bin_content)
            bin_errors = {"lo": np.zeros(size), "hi": np.zeros(size)}
        norm_data  = h_data.bin_content.sum()
        norm_pdf1  = h_pdf.bin_content.sum()
        norm_pdf2  = h_pdf_data_binning.bin_content.sum()
        hist_data = {
            'data': {
                'x': h_data.bin_center,
                'y': h_data.bin_content,
                'yerrlo': bin_errors['lo'],
                'yerrhi': bin_errors['hi']
            },
            'pdf': {
                'x': h_pdf.bin_center,
                'y': h_pdf.bin_content * norm_data / norm_pdf1 * (n_bins_pdf / n_bins_data)
            },
            'pdf_data_binning': {
                'x': h_pdf_data_binning.bin_center,
                'y': h_pdf_data_binning.bin_content * norm_data / norm_pdf2
            }
        }
        return hist_data
        

    def run(self, fname:str, tree_name:str, save_summary_as:Optional[str]=None, 
            save_param_as:Optional[str]=None, save_plot_as:Optional[str]=None):
        export_hist_data = save_plot_as is not None
        summary = self._run(fname, tree_name, model_class=self.model_class, 
                            param_templates=self.param_templates,
                            fit_options=self.fit_options,
                            plot_options=self.plot_options,
                            save_summary_as=save_summary_as,
                            save_param_as=save_param_as,
                            save_plot_as=save_plot_as)
        return summary
    
    @semistaticmethod
    def create_plot(self, data, outname:str, xlabel:Optional[str]=None,
                    ylabel:Optional[str]=None, param_data:Optional[Dict]=None,
                    stat_data:Optional[Dict]=None, plot_comparison:bool=True,
                    comparison_mode:str="difference", styles:Optional[Dict]=None,
                    annotations:Optional[List]=None):
        from quickstats.plots import PdfDistributionPlot
        label_map = {
            "pdf": "fit"
        }
        plotter = PdfDistributionPlot(data, label_map=label_map, styles=styles)
        annotation = {}
        if param_data is not None:
            annotation["params"] = param_data
        if stat_data is not None:
            annotation["stats"] = stat_data
        if annotation:
            plotter.set_annotation(**annotation)
        if plot_comparison:
            comparison_options = {
                "reference": "data",
                "target": "pdf_data_binning",
                "mode": comparison_mode
            }
        else:
            comparison_options = None
        if (ylabel is not None) and "bin_width" in ylabel:
            bin_width = np.unique(np.diff(data['data']['x']))
            if (len(bin_width) > 1) and (not np.allclose(bin_width, bin_width[0])):
                raise RuntimeError("can not deduce bin width: non-uniform binnings detected")
            bin_width = bin_width[0]
            ylabel = ylabel.format(bin_width=bin_width)
            
        if isinstance(annotations, dict):
            plotter.add_annotation(**annotations)
        elif isinstance(annotations, list):
            for annotation in annotations:
                plotter.add_annotation(**annotation)
        ax = plotter.draw(xlabel=xlabel, ylabel=ylabel, targets=["data", "pdf"],
                          comparison_options=comparison_options)
        import matplotlib.pyplot as plt
        plt.savefig(outname, bbox_inches="tight")
    
    @staticmethod
    def _get_iter_save_paths(fnames:List[str], save_paths:Optional[Union[List[str], str]]=None):
        # do not save
        if save_paths is None:
            return repeat(None)
        # save by expressionn
        elif isinstance(save_paths, str):
            _save_paths = []
            for fname in fnames:
                basename = os.path.basename(fname)
                _save_paths.append(fname.format(basename=basename))
            return _save_paths
        # save by explicit paths
        elif isinstance(save_paths, list):
            if len(fnames) != len(save_paths):
                raise RuntimeError("number of output file paths must match the number input files")
            return save_paths
        else:
            raise ValueError("invalid save option")
        
    def batch_run(self, fnames:List[str], tree_name:str,
                  save_summary_as:Optional[Union[List[str], str]]=None,
                  save_param_as:Optional[Union[List[str], str]]=None,
                  save_plot_as:Optional[Union[List[str], str]]=None,
                  plot_options:Optional[List]=None, parallel:int=-1):
        self.sanity_check()
        save_summary_as = self._get_iter_save_paths(fnames, save_summary_as)
        save_param_as   = self._get_iter_save_paths(fnames, save_param_as)
        save_plot_as    = self._get_iter_save_paths(fnames, save_plot_as)
        if plot_options is None:
            plot_options = repeat(self.plot_options)
        elif isinstance(plot_options, dict):
            plot_options = repeat(combine_dict(self.plot_options, plot_options))
        elif isinstance(plot_options, list):
            plot_options = [combine_dict(self.plot_options, _plot_options) for _plot_options in plot_options]
        else:
            raise ValueError("invalid plot options")
        args = (fnames, repeat(tree_name), repeat(self.model_class),
                repeat(self.param_templates), repeat(self.fit_options),
                plot_options, save_summary_as, save_param_as, 
                save_plot_as)
        results = execute_multi_tasks(self._run, *args, parallel=parallel)
        return results
    
    def run_over_categories(self, prefix:str, categories:List[str],
                            tree_name:str, input_dir:str="./",
                            save_summary_as:Optional[Union[List[str], str]]=None,
                            save_param_as:Optional[Union[List[str], str]]=None,
                            save_plot_as:Optional[Union[List[str], str]]=None,
                            save_merged_param_as:str="model_parameters.json",
                            plot_options:Optional[List]=None,
                            parallel:int=-1):
        fnames = []
        for category in categories:
            fname = os.path.join(input_dir, f"{prefix}_{category}.root")
            fnames.append(fname)

        results = self.batch_run(fnames, tree_name,
                                 save_summary_as=save_summary_as,
                                 save_param_as=save_param_as,
                                 save_plot_as=save_plot_as,
                                 plot_options=plot_options,
                                 parallel=parallel)
        category_results = dict(zip(categories, results))
        if save_merged_param_as is not None:
            param_data = {}
            for category, result in category_results.items():
                param_data[category] = self._get_simplified_param_data(result['parameters'])
            with open(save_merged_param_as, "w") as outfile:
                json.dump(param_data, outfile, indent=2)
        return category_results