from typing import Dict, Union, List, Optional

import numpy as np

import ROOT

from quickstats import semistaticmethod
from quickstats.interface.cppyy.vectorize import as_np_array

class RooDataSet:
    
    @staticmethod
    def to_numpy(dataset:ROOT.RooDataSet):
        components = dataset.get()
        observables = ROOT.RooArgSet()
        category = None
        for component in components:
            if component.ClassName() == "RooCategory":
                if category is not None:
                    raise RuntimeError("found multiple RooCategory instances")
                category = component
            else:
                observables.add(component)
        if category is None:
            result = ROOT.RFUtils.ExtractData(dataset, observables)
        else:
            result = ROOT.RFUtils.ExtractCategoryData(dataset, observables, category)
        obs_values = as_np_array(result.observable_values)
        n_entries = dataset.numEntries()
        data = {}
        for i, obs in enumerate(observables):
            obs_name = obs.GetName()
            data[obs_name] = obs_values[i*n_entries: (i + 1)*n_entries]
        data['weight'] = as_np_array(result.weights)
        if category is not None:
            data['label'] = as_np_array(result.category_labels)
            data['index'] = as_np_array(result.category_index)
        return data
    
    @staticmethod
    def from_numpy(data:Dict[str, "numpy.ndarray"],
                   variables:ROOT.RooArgSet,
                   name:str=None, title:str=None,
                   weight_name:str=None, clip_to_limits=True):
        if name is None:
            name = ""
        if title is None:
            title = ""
            
        if weight_name is None:
            dataset = ROOT.RooDataSet(name, title, variables)
        else:
            dataset = ROOT.RooDataSet(name, title, variables, weight_name)
            
        real_variables = {}
        cat_variables = {}
        for v in variables:
            var_name = v.GetName()
            class_name = v.ClassName()
            if var_name == weight_name:
                continue
            if var_name not in data:
                if (class_name == "RooCategory") and ("index" in data):
                    var_name = "index"
                else:
                    raise RuntimeError(f"missing data for the variable `{var_name}`")
            if class_name == "RooCategory":
                cat_variables[var_name] = v
            else:
                real_variables[var_name] = v
                if clip_to_limits:
                    data[var_name] = np.clip(data[var_name], 
                                             a_min=v.getMin(),
                                             a_max=v.getMax())
        if weight_name not in data:
            if "weight" in data:
                weight_name = "weight"
            else:
                raise RuntimeError(f"missing data for the variable `{weight_name}`")
        data_sizes = [len(data[k]) for k in data]
        if len(set(data_sizes)) > 1:
            raise RuntimeError("data has inconsistent sizes")
        if weight_name is None:
            for i in range(data_sizes[0]):
                for name, variable in real_variables.items():
                    variable.setVal(data[name][i])
                for name, variable in cat_variables.items():
                    variable.setIndex(data[name][i])
                dataset.add(variables, 1.)
        else:
            for i in range(data_sizes[0]):
                for name, variable in real_variables.items():
                    variable.setVal(data[name][i])
                for name, variable in cat_variables.items():
                    variable.setIndex(int(data[name][i]))
                weight = data[weight_name][i]
                dataset.add(variables, weight)
        return dataset
    
    @semistaticmethod
    def to_pandas(self, dataset:ROOT.RooDataSet):
        numpy_data = self.to_numpy(dataset, reduced=reduced)
        import pandas as pd
        df = pd.DataFrame(numpy_data)
        return df
    
    @staticmethod
    def get_dataset_map(dataset_dict:Dict):
        dsmap = ROOT.std.map('string, RooDataSet*')()
        dsmap.keepalive = list()
        for c, d in dataset_dict.items():
            dsmap.keepalive.append(d)
            dsmap.insert(dsmap.begin(), ROOT.std.pair("const string, RooDataSet*")(c, d))
        return dsmap
    
    @staticmethod
    def from_RooDataHist(source:ROOT.RooDataHist, pdf:ROOT.RooAbsPdf, name:Optional[str]=None):
        if name is None:
            name = source.GetName()
        parameters = source.get()
        category = None
        for parameter in parameters:
            if parameter.ClassName() == "RooCategory":
                category = parameter
                break
      # case multi-category data
        if category is not None:
            dataset_map = {}
            data_cat = source.split(category, True)
            n_cat = len(category)
            observables = ROOT.RooArgSet()
            for i in range(n_cat):
                category.setBin(i)
                cat_name = category.getLabel()
                pdf_i = pdf.getPdf(cat_name)
                data_i = data_cat.FindObject(cat_name)                
                obs_i = pdf_i.getObservables(data_i).first()
                _obs_i = data_i.get().find(obs_i.GetName())
                w_i = ROOT.RooRealVar(f"weight_{i}", f"weight_{i}", 1)
                dataset_i = ROOT.RooDataSet(f"dataset_{i}", f"dataset_{i}",
                                            ROOT.RooArgSet(obs_i, w_i),
                                            ROOT.RooFit.WeightVar(w_i))
                ROOT.RFUtils.CopyData(data_i, dataset_i, _obs_i, obs_i, w_i)
                dataset_map[cat_name] = dataset_i
                observables.add(obs_i)
            w = ROOT.RooRealVar("weight", "weight", 1)
            observables.add(w)
            cpp_dataset_map = RooDataSet.get_dataset_map(dataset_map)
            dataset = ROOT.RooDataSet(name, name, observables,
                                      ROOT.RooFit.Index(category),
                                      ROOT.RooFit.Import(cpp_dataset_map),
                                      ROOT.RooFit.WeightVar(w))
        # case single-category data
        else:
            obs = pdf.getObservables(source).first()
            _obs = source.get().find(obs.GetName())
            w = ROOT.RooRealVar("weight", "weight", 1)
            dataset = ROOT.RooDataSet(name, name, ROOT.RooArgSet(obs, w),
                                      ROOT.RooFit.WeightVar(w))
            ROOT.RFUtils.CopyData(source, dataset, _obs, obs, w)
        return dataset

    @staticmethod
    def _get_cat_and_obs(variables:ROOT.RooArgSet):
        cat_variable = None
        observables = {}
        for v in variables:
            class_name = v.ClassName()
            if class_name == "RooCategory":
                if cat_variable is not None:
                    raise RuntimeError("found multiple RooCategory instances")
                cat_variable = v
            else:
                var_name = v.GetName()
                observables[var_name] = v
        if cat_variable is None:
            raise RuntimeError("missing RooCategory instance from variables")
        return cat_variable, observables

    @semistaticmethod
    def create_binned_category_dataset(self, data:Dict[str, "numpy.ndarray"],
                                       pdf:ROOT.RooAbsPdf,
                                       variables:ROOT.RooArgSet,
                                       weight_name:str="weightVar",
                                       name:str=None, title:str=None):
        if name is None:
            name = ""
        if title is None:
            title = ""        
        cat_variable, observables = self._get_cat_and_obs(variables)
        n_cat = cat_variable.size()
        cat_names = []
        cat_obs_names = []
        for i in range(n_cat):
            cat_variable.setIndex(i)
            cat_name = cat_variable.getLabel()
            cat_names.append(cat_name)
            pdf_cat = pdf.getPdf(cat_name)
            obs = pdf_cat.getObservables(variables)
            cat_obs = obs.first()
            cat_obs_names.append(cat_obs.GetName())
        if set(cat_obs_names) != set(observables):
            raise RuntimeError("the given variables are insistent with the category observables")
        if not set(cat_names).issubset(set(data)):
            missing = list(set(cat_names) - set(data))
            raise RuntimeError("missing data for the following categories: {}".format(",".join(missing)))
        dataset = ROOT.RooDataSet(name, title, variables, weight_name)
        for i, (cat_name, obs_name) in enumerate(zip(cat_names, cat_obs_names)):
            observable = observables[obs_name]
            data_i = data[cat_name]
            cat_variable.setIndex(i)
            n_bins = observable.getBins()
            n_bins_data = len(data_i)
            if n_bins_data != n_bins:
                raise RuntimeError(f"the observable has `{n_bins}` bins but data has `{n_bins_data}`")
            for j in range(n_bins_data):
                observable.setBin(j)
                dataset.add(variables, data_i[j])
        return dataset
    
    @semistaticmethod
    def to_category_data(self, dataset:ROOT.RooDataSet,
                         pdf:ROOT.RooAbsPdf):
        variables = dataset.get()
        cat_variable, observables = self._get_cat_and_obs(variables)
        n_cat = cat_variable.size()
        data = self.to_numpy(dataset)
        result = {}
        for i in range(n_cat):
            cat_variable.setIndex(i)
            cat_name = cat_variable.getLabel()
            pdf_cat = pdf.getPdf(cat_name)
            obs = pdf_cat.getObservables(variables)
            cat_obs = obs.first()
            obs_name = cat_obs.GetName()
            mask = (data['index'] == i)
            bin_value = data[obs_name][mask]
            ind = np.argsort(bin_value)
            bin_weight = data['weight'][mask][ind]
            result[cat_name] = bin_weight
        return result