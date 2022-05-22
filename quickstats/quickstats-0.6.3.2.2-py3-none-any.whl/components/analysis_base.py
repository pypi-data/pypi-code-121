from typing import Optional, Union, List, Dict

from quickstats.components import AnalysisObject, Likelihood, AsimovGenerator

class AnalysisBase(Likelihood, AsimovGenerator):
    def __init__(self, filename:str, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:str='combData', 
                 config:Optional[Union[Dict, str]]=None,
                 verbosity:Optional[Union[int, str]]="INFO", **kwargs):
        super().__init__(filename=filename,
                         poi_name=poi_name,
                         data_name=data_name,
                         config=config,
                         verbosity=verbosity)
        
    def plot_fit_summary(self, uncond_fit:bool=True, cond_fit:bool=True,
                         categories:Optional[List[str]]=None, n_bins:int=None,
                         discriminant:Optional[str]=None, unit:Optional[str]=None,
                         save_as:Optional[str]=None, label_map:Optional[str]=None,
                         comparison_plot:bool=True,
                         comparison_options:Optional[Dict]=None,
                         **kwargs):
        data_name = self.model._data.GetName()
        snapshots = []
        if cond_fit:
            if not self.model.workspace.getSnapshot("condFit"):
                self.stdout.warning("WARNING: No conditional fit is made. The corresponding plot will not be shown")
            else:
                snapshots.append("condFit")
        if uncond_fit:
            if not self.model.workspace.getSnapshot("uncondFit"):
                self.stdout.warning("WARNING: No unconditional fit is made. The corresponding plot will not be shown")
            else:
                snapshots.append("uncondFit")
        kwargs = {
            **kwargs,
            "categories": categories,
            "current_distributions": False,
            "datasets": [data_name],
            "snapshots": snapshots,
            "blind": self.use_blind_range,
            "n_bins": n_bins,
            "save_as": save_as,
            "label_map": label_map,
            "discriminant": discriminant,
            "unit": unit
        }
        if kwargs['blind']:
            self.stdout.info("INFO: Using blinded fit result.")
        if comparison_plot:
            if comparison_options is None:
                comparison_options = {}
            comparison_options['reference'] = data_name
            if "target" not in comparison_options:
                if "uncondFit" in kwargs['snapshots']:
                    self.stdout.info("INFO: Using data vs unconditional fit for comparison plot")
                    comparison_options["target"] = "uncondFit"
                elif "condFit" in kwargs['snapshots']:
                    comparison_options["target"] = "condFit"
                else:
                    self.stdout.warning("WARNING: No fit results available. Comparison plot will not be made.")
                    comparison_options = None
            kwargs['comparison_options'] = comparison_options
        self.model.plot_distributions(**kwargs)