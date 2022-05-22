###############################################################################
### This is a reimplementation of xmlAnaWSBuilder library in python
### original author: Hongtao Yang
###############################################################################
import os
import time
from typing import Optional, Union, List, Dict

import numpy as np

import ROOT

from quickstats import semistaticmethod
from quickstats.components import AbstractObject, ExtendedModel
from quickstats.utils.io import Verbosity
from quickstats.utils.xml_tools import TXMLTree
from quickstats.utils.common_utils import remove_list_duplicates, format_delimiter_enclosed_text
from quickstats.maths.numerics import is_float, pretty_value

from quickstats.components.workspaces import XMLWSBase, Sample, Systematic, AsimovHandler
    
class XMLWSBuilder(XMLWSBase):
    
    EPSILON = 1e-6
    
    KEYWORDS = {
        # likelihood model
        "response": "response::",
        "observable": ":observable:",
        "process": ":process:",
        "common": ":common:",
        "self": ":self:",
        "category": ":category:",
        # C++ logics
        "lt": ":lt:",
        "le": ":le:",
        "gt": ":gt:",
        "ge": ":ge:",
        "and": ":and:",
        "or": ":or:",
        # operations
        "allproc": "_allproc_",
        "yield": "yield",
        "shape": "shape",
        "counting": "counting",
        # data_source
        "ascii": "ascii",
        "histogram": "histogram",
        # pdf
        "userdef": "userdef",
        "external": "external",
        # constraint
        "gaussian": "gaus",
        "logn": "logn",
        "asym": "asym",
        "dfd": "dfd",
        # naming
        "response_prefix": "expected__",
        "constrterm_prefix": "constr__",
        "globalobs_prefix": "RNDM__",
        "variationhi_prefix": "varHi__",
        "variationlo_prefix": "varLo__",
        "yield_prefix": "yield__",
        "pdf_prefix": "pdf__",
        "expectation_prefix": "expectation__",
        "sum_pdf_name": "_modelSB",
        "final_pdf_name": "_model",
        "lumi_name": "_luminosity",
        "xs_name": "_xs",
        "br_name": "_br",
        "norm_name": "_norm",
        "acceptance_name": "_A",
        "correction_name": "_C",
        "efficiency_name": "_eff",
        "obs_ds_name": "obsData",
        # blinding
        "sb_lo": "SBLo",
        "sb_hi": "SBHi",
        "blind": "Blind",
        "uncert_hi_prefix": "uncertHi__",
        "uncert_lo_prefix": "uncertLo__",
        "uncert_sym_prefix": "uncertSymm__",
        "uncert_other_prefix": "unknwon",
        # snapshots
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
    
    def __init__(self, source:str, basedir:Optional[str]=None,
                 use_binned:bool=False,
                 data_storage_type:str="vector",
                 minimizer_config:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(source=source, basedir=basedir, verbosity=verbosity)
        self.use_binned = use_binned
        self.data_storage_type = data_storage_type
        self.minimizer_config = minimizer_config
        self.load_extension()
        self.initialize(source=source)
    
    @staticmethod
    def set_data_storage_type(data_storage_type:str="vector"):
        if data_storage_type == "tree":
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Tree)
        elif data_storage_type == "vector":
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Vector)
        elif data_storage_type == "composite":
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Composite)            
        else:
            raise RuntimeError(f"unknown data storage type `{data_storage_type}`")
  
    def initialize(self, source:str):
        self.core_config = self.parse_core_xml(source)
        self._print_core_xml_summary()
        self.cat_config = {}
        self.cat_ws = {}
        self.datahists = {}
        self.datasets = {}
        self.datasets_binned = {}
        self.time_taken = 0.
        ws_name = self.core_config['workspace_name']
        mc_name = self.core_config['model_config_name']
        self.set_data_storage_type(self.data_storage_type)
        self.comb_ws = ROOT.RooWorkspace(ws_name)
        self.model_config = ROOT.RooStats.ModelConfig(mc_name, self.comb_ws)
    
    @semistaticmethod
    def _xml_to_dict(self, filename:str):
        try:
            xml_dict = TXMLTree(file=filename).to_dict()
        except:
            raise RuntimeError(f"failed to load xml document `{filename}`")
        return xml_dict
    
    def parse_core_xml(self, filename:str):
        self.stdout.info(f"INFO: Parsing file `{filename}`")
        # load xml file
        core_xml = self._xml_to_dict(filename)
        # parse basic attributes
        attributes = core_xml['attrib']
        content = {
            'base_dir': os.path.dirname(filename),
            'workspace_name': attributes['WorkspaceName'],
            'model_config_name': attributes['ModelConfigName'],
            'dataset_name': attributes['DataName'],
            'output_name': attributes['OutputFile'],
            'do_blind': int(attributes.get('Blind', "0")),
            'integrator': attributes.get('Integrator', ""),
            'poi_names': [],
            'input_categories': [],
            'asimov_definitions': []
        }
        if not content['output_name'].endswith(".root"):
            content['output_name'] = os.path.splitext(content['output_name'])[0] + ".root"
            self.stdout.info("WARNING: Output file name does not contain \".root\" postfix. "
                             "Adding it to avoid confusion.")
        # parse child level attributes
        nodes = core_xml['children']
        for node in nodes:
            tag = node['tag']
            if tag == "Input":
                input_filename = node['text']
                content['input_categories'].append(input_filename)
            elif tag == "POI":
                poi_expr = node['text']
                content['poi_names'] += poi_expr.split(",")
            elif tag == "Asimov":
                definitions = node['attrib']
                content['asimov_definitions'].append(definitions)
            else:
                raise RuntimeError(f"unknown item `{tag}`")
        return content
        
    def _print_core_xml_summary(self):
        if not self.core_config:
            raise RuntimeError("core config not set")
        self.stdout.info("=========================================================================")
        self.stdout.info("Output file: ".rjust(20) + f"{self.core_config['output_name']}")
        self.stdout.info("Workspace name: ".rjust(20) + f"{self.core_config['workspace_name']}")
        self.stdout.info("ModelConfig name: ".rjust(20) + f"{self.core_config['model_config_name']}")
        self.stdout.info("Dataset name: ".rjust(20) + f"{self.core_config['dataset_name']}")
        self.stdout.info("Bline analysis: ".rjust(20) + ("True" if self.core_config['do_blind'] else "False"))
        self.stdout.info("POIs: ".rjust(20) + ", ".join(self.core_config['poi_names']))
        self.stdout.info("")
        self.stdout.info("Categories to be included:")
        input_categories = self.core_config['input_categories']
        for i,input_category in enumerate(input_categories):
            self.stdout.info(f"XML file {i}: ".rjust(20) + f"{input_category}")
        asimov_definitions = self.core_config['asimov_definitions']
        if asimov_definitions:
            self.stdout.info("")
            self.stdout.info("The following asimov dataset(s) will be generated:")
            for asimov_def in asimov_definitions:
                is_gen_asimov = self.KEYWORDS['gen_asimov'] in asimov_def['Action']
                if is_gen_asimov:
                    asimov_name = asimov_def['Name']
                    self.stdout.info(f"\t{asimov_name}")
        self.stdout.info("=========================================================================")
    
    def generate_workspace(self):
        t0 = time.time()
        channel_list = ROOT.RooCategory("channellist", "channellist")
        combined_pdf = ROOT.RooSimultaneous("CombinedPdf", "", channel_list)
        
        pois           = ROOT.RooArgSet()
        nuis           = ROOT.RooArgSet()
        globobs        = ROOT.RooArgSet()
        constraints    = ROOT.RooArgSet()
        observables    = ROOT.RooArgSet()
        
        self.cat_config      = {}
        self.cat_ws          = {}
        self.datahists       = {}
        self.datasets        = {}
        self.datasets_binned = {}
        self.time_taken      = 0.
        
        inputfiles = self.core_config['input_categories']
        
        for i, inputfile in enumerate(inputfiles):
            ws_name = f"wchannel_{i}"
            ws_i = self.generate_single_category(inputfile, ws_name)
            
            category = self.current_category
            self.cat_ws[category] = ws_i
            
            channel_list.defineType(category)
            pdf_name = f"{self.KEYWORDS['final_pdf_name']}_{category}"
            pdf_i = ws_i.pdf(pdf_name)
            if not pdf_i:
                raise RuntimeError(f"model pdf `{pdf_name}` for the category "
                                   f"`{category}` not defined")
            combined_pdf.addPdf(pdf_i, category)
            
            nuis.add(ws_i.set("nuisanceParameters"), True)
            globobs.add(ws_i.set("globalObservables"), True)
            observables.add(ws_i.set("Observables"), True)
            pois.add(ws_i.set("POI"), True)
            
            if self.debug_mode:
                ws_i.Print()
        #observables.add(channel_list)
        self.import_object(self.comb_ws, combined_pdf)
        
        self.comb_ws.defineSet("nuisanceParameters", nuis)
        self.comb_ws.defineSet("globalObservables", globobs)
        self.comb_ws.defineSet("Observables", observables)        
        self.comb_ws.defineSet("POI", pois)
        
        self.model_config.SetPdf(self.comb_ws.pdf("CombinedPdf"))
        self.model_config.SetObservables(self.comb_ws.set("Observables"))
        self.model_config.SetParametersOfInterest(self.comb_ws.set("POI"))
        self.model_config.SetNuisanceParameters(self.comb_ws.set("nuisanceParameters"))
        self.model_config.SetGlobalObservables(self.comb_ws.set("globalObservables"))
        self.import_object(self.comb_ws, self.model_config, silent=False)
        
        weight_var = ROOT.RooRealVar("wt", "wt", 1)
        args = ROOT.RooArgSet()
        args.add(observables)
        args.add(weight_var)
        
        dataset_map = ExtendedModel.get_dataset_map(self.datasets)
        dataset_binned_map = ExtendedModel.get_dataset_map(self.datasets_binned)
        
        dataset_name = self.core_config['dataset_name']
        obs_data = ROOT.RooDataSet(dataset_name, "Combined data", args,
                                   ROOT.RooFit.Index(channel_list),
                                   ROOT.RooFit.Import(dataset_map),
                                   ROOT.RooFit.WeightVar(weight_var))
        obs_data_binned = ROOT.RooDataSet(dataset_name + "binned", 
                                          "Binned combined data", args,
                                          ROOT.RooFit.Index(channel_list),
                                          ROOT.RooFit.Import(dataset_binned_map),
                                          ROOT.RooFit.WeightVar(weight_var))
        self.import_object(self.comb_ws, obs_data, silent=False)
        if (obs_data_binned.numEntries() < obs_data.numEntries()):
            self.import_object(self.comb_ws, obs_data_binned, silent=False)
        else:
            self.stdout.warning("REGTEST: No need to keep binned dataset, as the "
                                "number of data events is smaller than or equal "
                                "to the number of bins in all categories", "red")
            self.use_binned = False
        
        # save the original snapshot
        # self.comb_ws.saveSnapshot("nominalNuis", self.model_config.GetNuisanceParameters())
        # self.comb_ws.saveSnapshot("nominalGlobs", self.model_config.GetGlobalObservables())
        
        # generate asimov datasets
        self.generate_asimov()
        
        # save final workspace
        output_path = self.get_output_path()
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.comb_ws.writeToFile(output_path, True)
        
        t1 = time.time()
        self.time_taken += (t1 - t0)
        self.print_final_summary()
    
    def print_final_summary(self):
        ws_name = self.comb_ws.GetName()
        model = ExtendedModel(self.comb_ws, data_name=self.core_config['dataset_name'], verbosity="WARNING")
        pdf = model.pdf
        cat = pdf.indexCat()
        n_cat = len(cat)
        data = model.data
        data_list = data.split(cat, True)
        # start writing summary
        self.stdout.info("="*70)
        title_str = format_delimiter_enclosed_text("Begin summary", "~")
        self.stdout.info(title_str)
        self.stdout.info(f"\tThere are {n_cat} sub channels:")
        for i in range(n_cat):
            cat.setBin(i)
            cat_name = cat.getLabel()
            pdf_i = pdf.getPdf(cat_name)
            data_i = data_list.FindObject(cat_name)
            sum_entries = pretty_value(data_i.sumEntries(), 5)
            self.stdout.info(f"\t\tIndex: {i}, Pdf: {pdf_i.GetName()}, Data: {data_i.GetName()}, SumEntries: {sum_entries}")
        title_str = format_delimiter_enclosed_text("POI", "-")
        self.stdout.info(title_str)
        if Verbosity.INFO >= self.stdout.verbosity:
            model.pois.Print("v")
        title_str = format_delimiter_enclosed_text("Dataset", "-")
        self.stdout.info(title_str)
        if Verbosity.INFO >= self.stdout.verbosity:
            for dataset in model.workspace.allData():
                dataset.Print()
        title_str = format_delimiter_enclosed_text("End Summary", "~")
        self.stdout.info(title_str)
        output_path = self.get_output_path()
        self.stdout.info(f"Workspace `{ws_name}` has been successfully generated and saved in file `{output_path}`")
        #output_plot_path = self.get_output_plot_path()
        #self.stdout.info(f"Plots for each category are summarized in `{output_plot_path}`")
        self.stdout.info(f"Total time taken: {self.time_taken:.3f}s")
        self.stdout.info("="*70)
    
    def get_output_path(self):
        output_name = self.core_config['output_name']
        output_path = self.get_relpath(output_name)
        return output_path
    
    def get_output_plot_path(self):
        output_path = self.get_output_path()
        output_plot_path = os.path.splitext(output_path)[0] + ".pdf"
        return output_plot_path
                         
    def generate_asimov(self):
        n_asimov = len(self.core_config['asimov_definitions'])
        if n_asimov == 0:
            return None
        if self.use_binned:
            data_name = self.core_config['dataset_name'] + "binned"
            self.stdout.warning("REGTEST: Fitting binned dataset.", "red")
        else:
            data_name = self.core_config['dataset_name']
        ws = self.comb_ws
        range_name = self.get_fit_range_name()
        asimov_handler = AsimovHandler(ws, data_name=data_name, range_name=range_name,
                                       minimizer_config=self.minimizer_config)
        for attributes in self.core_config['asimov_definitions']:
            asimov_handler.generate_single_asimov(attributes)
        
    def get_fit_range_name(self):
        do_blind = self.core_config['do_blind']
        if do_blind:
            return self.get_sideband_range_name()
        else:
            return None
        
    def get_sideband_range_name(self):
        """Get sideband range name to be used in fitting
        """
        range_name_SBLo = self.KEYWORDS['sb_lo']
        range_name_SBHi = self.KEYWORDS['sb_hi']
        return f"{range_name_SBLo},{range_name_SBHi}"
    
    def get_blind_range_name(self):
        """Get blind range name that are excluded from the fit range
        """
        return self.KEYWORDS['blind']        
        
    def generate_single_category(self, filename:str, workspace_name:str):
        ws = ROOT.RooWorkspace(workspace_name)
        nuis           = ROOT.RooArgSet()
        globobs        = ROOT.RooArgSet()
        constraints    = ROOT.RooArgSet()
        expected       = ROOT.RooArgSet()
        expected_shape = ROOT.RooArgSet()
        expected_map   = {}
        # load xml file
        filepath = self.get_relpath(filename)
        cat_xml = self._xml_to_dict(filepath)
        attributes = cat_xml['attrib']
        nodes = cat_xml['children']
        category_name = attributes['Name']
        if category_name in self.cat_config:
            raise RuntimeError(f"duplicated category name: `{category_name}`")
            
        title_str = format_delimiter_enclosed_text(f"Category {category_name}", "-")
        self.stdout.info(title_str)
        
        self.current_category = category_name
        category_type = attributes['Type'].lower()
        luminosity = float(self._get_node_attrib(cat_xml, "Lumi", False, "-1"))
        
        self.cat_config[category_name] = {
            'input_file': filename,
            'category_type': category_type,
            'luminosity': luminosity,
            'observable': {
                'name': ""
            }
        }
        ws_factory = ROOT.RooWorkspace(f"factory_{category_name}")
        
        # define lumi
        if luminosity > 0:
            lumi_expr = f"{self.KEYWORDS['lumi_name']}[{luminosity}]"
            self.import_expression(ws_factory, lumi_expr)

        # define dataset
        data_node = self.fetch_node(nodes, "Data", xml_filename=filename, xml_type="channel",
                                    allow_multiple=False, allow_missing=False)
        self.read_data_node(data_node, ws_factory)
        
        # define correlation terms        
        correlate_node = self.fetch_node(nodes, "Correlate", xml_filename=filename, xml_type="channel",
                                         allow_multiple=False, allow_missing=True)
        self.read_correlate_node(correlate_node)
        
        self.cat_config[category_name]['items_highpriority'] = []
        self.cat_config[category_name]['items_lowpriority'] = []
        self.cat_config[category_name]['systematics'] = {}
        self.cat_config[category_name]['samples'] = []

        remained_nodes = [node for node in nodes if node['tag'] not in ["Data", "Correlate"]]
        self.read_channel_xml_nodes(remained_nodes, ws_factory)
 
        self._fix_item_priority()
        items_highpriority  = self.cat_config[category_name]['items_highpriority']
        items_lowpriority   = self.cat_config[category_name]['items_lowpriority']
        
        self.stdout.debug("REGTEST: High priority items:")
        for item in items_highpriority:
            self.stdout.debug(f"\t{item}")
        self.stdout.debug("REGTEST: Low priority items:")
        for item in items_lowpriority:
            self.stdout.debug(f"\t{item}")
        # first implement high priority items: common variables 
        # and functions not involving systematic uncertainties
        self.import_expressions(ws_factory, items_highpriority)

        systematics = self.cat_config[category_name]['systematics']
        samples = self.cat_config[category_name]['samples']
        # secondly implement systematics and import them into the workspace
        for domain in systematics:
            syst_list = systematics[domain]
            if domain == self.KEYWORDS['allproc']:
                resp_collection_yield = expected
            else:
                sample = [s for s in samples if s.is_equal(domain)]
                if sample:
                    resp_collection_yield = sample[0].expected
                else:
                    if domain not in expected_map:
                        expected_map[domain] = ROOT.RooArgSet()
                    resp_collection_yield = expected_map[domain]
            for syst in syst_list:
                if syst.whereto == self.KEYWORDS['yield']:
                    res_collection = resp_collection_yield
                elif syst.whereto == self.KEYWORDS['shape']:
                    res_collection = expected_shape
                else:
                    raise RuntimeError(f"unknown location `{syst.whereto}` for "
                                       f"the systematic `{syst.name}`. Choose between "
                                       f"`{self.KEYWORDS['yield']}` or `{self.KEYWORDS['shape']}`")
                self.make_np(ws_factory, syst, nuis, constraints, globobs, res_collection)

        # work on remaining common variables and functions to be implemented
        self.import_expressions(ws_factory, items_lowpriority)
        
        if self.debug_mode:
            ws_factory.Print()
        
        # organize the scale factors on each sample
        if (expected.getSize() > 0):
            expr = self._generate_expr(f"prod::{self.KEYWORDS['expectation_prefix']}common(", expected)
            self.import_expression(ws_factory, expr)
        for key, value in expected_map.items():
            expr = self._generate_expr(f"prod::{self.KEYWORDS['expectation_prefix']}{key}(", value)
            self.import_expression(ws_factory, expr)
            
        for sample in samples:
            title_str = format_delimiter_enclosed_text(sample.process, "<", 20)
            self.stdout.debug(title_str)
            self.import_expressions(ws_factory, sample.shape_factors)
            sample.norm_name = self.KEYWORDS['yield_prefix'] + sample.process
            norm_factor_components = []
            norm_factor_comp = self.import_expressions(ws_factory, sample.norm_factors)
            norm_factor_components.append(norm_factor_comp)
            
            if sample.expected.getSize() > 0:
                expectation_expr = self._generate_expr(f"prod::{self.KEYWORDS['expectation_prefix']}proc_{sample.process}(",
                                                      sample.expected)
                expectation_str = self.import_expression(ws_factory, expectation_expr)
                norm_factor_components.append(expectation_str)
            
            # if :self: appears anywhere, do not do anything
            if self.KEYWORDS['self'] not in sample.syst_groups:
                for syst_group in sample.syst_groups:
                    if syst_group == self.KEYWORDS['allproc']:
                        if expected.getSize() > 0:
                            norm_factor_comp = f"{self.KEYWORDS['expectation_prefix']}common"
                            norm_factor_components.append(norm_factor_comp)
                    else:
                        if syst_group in expected_map:
                            norm_factor_comp = f"{self.KEYWORDS['expectation_prefix']}{syst_group}"
                            norm_factor_components.append(norm_factor_comp)
                        else:
                            raise RuntimeError(f"unknwon systematic group `{syst_group}` in "
                                               f"Sample `{sample.process}`")
            norm_comp_str = ",".join(norm_factor_components)
            norm_str = f"prod::{sample.norm_name}({norm_comp_str})"
            self.import_expression(ws_factory, norm_str)
            proc_yield = ws_factory.function(sample.norm_name).getVal()
            self.stdout.info(f"REGTEST: Yield for category `{category_name}` "
                             f"process `{sample.process}`: {proc_yield}")
            if self.debug_mode:
                ws_factory.Print()
            
            self.get_model(ws_factory, sample, nuis, constraints, globobs)
        
        if self.debug_mode:
            ws_factory.Print()
        
        # generate the combined pdf
        sum_pdf_components = [f"{sample.norm_name}*{sample.model_name}" for sample in samples]
        sum_pdf_str = f"SUM::{self.KEYWORDS['sum_pdf_name']}({','.join(sum_pdf_components)})"
        self.stdout.debug(f"REGTEST: Sum pdf expr = {sum_pdf_str}")
        self.import_expression(ws_factory, sum_pdf_str)
        SB_pdf = ws_factory.pdf(self.KEYWORDS['sum_pdf_name'])

        self.implement_blind_range(ws_factory)
        
        self.check_nuisance_parameters(SB_pdf, nuis)
        
        # keep track of correlated variables
        correlated_terms = self.get_correlated_terms(ws_factory, nuis)
        correlated_str = ",".join(correlated_terms)
        
        self.stdout.debug(f"REGTEST: The following variables will not be renamed: {','.join(correlated_terms)}")
        # import pdf to new workspace, rename objects as appropriate
        self.import_object(ws, ws_factory.pdf(self.KEYWORDS['sum_pdf_name']),
                           ROOT.RooFit.RenameAllNodes(category_name),
                           ROOT.RooFit.RenameAllVariablesExcept(category_name, correlated_str))
        
        # import constraint terms
        self.attach_constraints(ws, constraints)
        
        obs = self.get_observable(ws)
        # define variable sets
        poi_names = self.get_poi_names()
        self._define_set(ws, poi_names, "POI")
        self._define_set(ws, nuis, "nuisanceParameters")
        self._define_set(ws, globobs, "globalObservables")
        obs_set = ROOT.RooArgSet(obs)
        self._define_set(ws, obs_set, "Observables")
        
        if self.debug_mode:
            ws.Print()
            
        weight_var = ROOT.RooRealVar("wt", "wt", 1)
        dataset, datahist = self.generate_dataset(obs, weight_var)
    
        # prepare binned data
        dataset_binned_name = self.KEYWORDS['obs_ds_name'] + "binned"
        dataset_binned = dataset.Clone(dataset_binned_name)
        
        # consider that blinded analysis the number of bins will reduce
        do_blind = self.core_config['do_blind']
        blind_range = self.cat_config[category_name]['dataset']['blind_range']
        blind_sf = 1
        if do_blind and blind_range:
            blind_sf = 1 - (blind_range[1] - blind_range[0]) / (obs.getMax() - obs.getMin())
        if (dataset.numEntries() > (obs.numBins() * blind_sf)):
            dataset_binned = ROOT.RooDataSet(dataset_binned_name, dataset_binned_name,
                                             ROOT.RooArgSet(obs, weight_var),
                                             ROOT.RooFit.WeightVar(weight_var))
            self._fill_dataset_from_hist(dataset_binned, datahist, obs, weight_var)
        num_events = pretty_value(dataset.sumEntries(), 5)
        self.stdout.info(f"REGTEST: Number of data events: {num_events}")
        self.import_object(ws, dataset)
        self.import_object(ws, dataset_binned)
        
        self.datahists[category_name]       = datahist
        self.datasets[category_name]        = dataset
        self.datasets_binned[category_name] = dataset_binned
        
        return ws

    @staticmethod
    def _define_set(ws:ROOT.RooWorkspace, arg_set:Union[ROOT.RooArgSet, List[str]], name:str):
        proper_set = ROOT.RooArgSet()
        for var in arg_set:
            if not isinstance(var, str):
                var_name = var.GetName()
                ws_var = ws.var(var_name)
            else:
                ws_var = ws.var(var)
            if (ws_var):
                proper_set.add(ws_var)
        ws.defineSet(name, proper_set)
        
    def generate_dataset(self, obs:ROOT.RooRealVar, weight_var:ROOT.RooRealVar):
        category_name = self.current_category
        cat_config = self.get_active_category_config()
        data_config = cat_config['dataset']
        obs_min = obs.getMin()
        obs_max = obs.getMax()
        n_bins = obs.getBins()
        data_scale = data_config['scale_data']
        data_name = self.KEYWORDS['obs_ds_name']
        filename = data_config['filename']
        filepath = self.get_relpath(filename)
        filetype = data_config['filetype']
        obs_plus_weight = ROOT.RooArgSet(obs, weight_var)
        
        dataset = ROOT.RooDataSet(data_name, data_name, obs_plus_weight,
                                  ROOT.RooFit.WeightVar(weight_var))
        datahist = ROOT.TH1D(category_name, category_name, n_bins, obs_min, obs_max)
        datahist.Sumw2()
        
        is_counting = cat_config['category_type'] == self.KEYWORDS['counting']
        num_data = data_config['num_data']
        
        # counting experiment
        if (is_counting and num_data >= 0):
            bin_center = (obs_min + obs_max) / 2.
            if num_data == 0:
                weight = self.EPSILON / 1000.
            else:
                weight = num_data * data_scale
            obs.setVal(bin_centee)
            weight_var.setVal(weight)
            dataset.add(ROOT.RooArgSet(obs, weight_var), weight)
            datahist.Fill(bin_ceeer, weight)
        #  histogram
        elif (filetype == self.KEYWORDS['histogram']):
            histname = data_config['histname']
            h = self.get_histogram(filename, histname)
            for i in range(1, h.GetNbinsX() + 1):
                if h.GetBinContent(i) < 0:
                    self.stdout.warning(f"REGTEST: Input data histogram bin {i} in "
                                        f"category {category_name} has negative weight. "
                                        f"Will force it to zero.", "red")
                    h.SetBinContent(i, 0)
                    h.SetBinError(i, 0)
            
            self._fill_dataset_from_hist(dataset, h, obs, weight_var, data_scale)
            
            self._rebin_hist_to_obs(h, obs)
            
            bin_low, bin_high, n_bins = self._find_bins_wrt_obs(h, obs)
            obs_n_bins = obs.getBins()
            for i in range(1, obs_n_bins + 1):
                bin_index = bin_low + i - 1
                bin_content = h.GetBinContent(bin_index) * data_scale
                bin_error = h.GetBinError(bin_index) * data_scale
                datahist.SetBinContent(i, bin_content)
                datahist.SetBinError(i, bin_error)
            n_event = dataset.sumEntries()
            n_event_binned = datahist.Integral()
            if abs(n_event - n_event_binned) > self.EPSILON:
                raise RuntimeError(f"Binned ({n_event_binned}) and unbinned ({n_event}) "
                                   f"datasets have different number of entries in "
                                   f"category {category_name}")
        else:
            if filetype == self.KEYWORDS['ascii']:
                filepath = self.get_relpath(filename)
                dataset_tmp = ROOT.RooDataSet.read(filepath, ROOT.RooArgList(obs))
            else:
                cut      = data_config['cut']
                treename = data_config['treename']
                varname  = data_config['varname']
                chain, _ = self.get_chain_and_branch(filepath, treename, varname, cut)
                x_tree = ROOT.RooRealVar(varname, varname, obs.getMin(), obs.getMax())
                _dataset_name = f"{self.KEYWORDS['obs_ds_name']}_tmp"
                dataset_tmp = ROOT.RooDataSet(_dataset_name, _dataset_name,
                                              ROOT.RooArgSet(x_tree),
                                              ROOT.RooFit.Import(chain))
            xdata_tmp = dataset_tmp.get().first()
            do_blind = self.core_config['do_blind']
            blind_range = data_config['blind_range']            
            for i in range(dataset_tmp.numEntries()):
                dataset_tmp.get(i)
                x_val = xdata_tmp.getVal()
                obs.setVal(x_val)
                weight = dataset_tmp.weight() * data_scale
                weight_var.setVal(weight)
                # ignore data in the blind range
                if (do_blind and blind_range) and (x_val > blind_range[0]) and (x_val < blind_range[1]):
                    continue
                dataset.add(ROOT.RooArgSet(obs, weight_var), weight)
                datahist.Fill(x_val, weight)
        if self.debug_mode:
            dataset.Print("v")
        # inject ghost
        inject_ghost = data_config['inject_ghost']
        if inject_ghost:
            self.release_ghost(dataset, datahist, obs, weight_var, self.EPSILON / 1000.)
        return dataset, datahist
    
    def _rebin_hist_to_obs(self, h:ROOT.TH1, obs:ROOT.RooRealVar):
        category = self.current_category
        bin_low, bin_high, n_bins = self._find_bins_wrt_obs(h, obs)
        obs_n_bins = obs.getBins()
        if n_bins != obs_n_bins:
            if n_bins == 0:
                histname = h.GetName()
                raise RuntimeError(f"input data histogram `{histname}` in category "
                                   f"{category} has a computed number of bins equal "
                                   f"to 0, please check compatibility between your "
                                   f"observable and the histogram range")
            if (n_bins < obs_n_bins):
                raise RuntimeError(f"input data histogram `{histname}` in category "
                                   f"{category} has fewer bins ({n_bins}) compared "
                                   f"to observable ({obs_n_bins})")
            if (n_bins > obs_n_bins) and (n_bins % obs_n_bins != 0):
                raise RuntimeError(f"input data histogram `{histname}` in category "
                                   f"{category} has inconsistent number of bins "
                                   f"({n_bins}) compared to observable ({obs_n_bins})")
            else:
                self.stdout.warning(f"REGTEST: Rebinning input data histogram "
                                    f"`{histname}` in category {category} by "
                                    f"{n_bins // obs_n_bins} to match the "
                                    f"binning of observable")
                h.Rebin(n_bins // obs_n_bins)
                
    @staticmethod
    def _find_bin(h:ROOT.TH1, low_edge:float):
        h_first_bin = h.GetBinLowEdge(1)
        if (low_edge < h_first_bin) and abs(low_edge - h_first_bin > self.EPSILON):
            return 0
        n_bins = h.GetNbinsX()
        h_last_bin = h.GetBinLowEdge(n_bins)
        if (low_edge > h_last_bin) and abs(low_edge - h_last_bin > self.EPSILON):
            return n_bins + 1
        for i in range(1, n_bins + 1):
            bin_edge = h.GetBinLowEdge(i)
            if abs(bin_edge - low_edge) < self.EPSILON:
                return i
        return -1
        
    @semistaticmethod
    def _find_bins_wrt_obs(self, h:ROOT.TH1, obs:ROOT.RooRealVar):
        obs_min = obs.getMin()
        obs_max = obs.getMax()
        bin_low = self._find_bin(h, obs_min)
        bin_high = self._find_bin(h, obs_max)
        n_bins = bin_high - bin_low
        return bin_low, bin_high, n_bins
    
    def _fill_dataset_from_hist(self, dataset:ROOT.RooDataSet, h:ROOT.TH1,
                                x:ROOT.RooRealVar, w:ROOT.RooRealVar, scale:float=1):
        # blinding will be taken care of
        xmin = x.getMin()
        xmax = x.getMax()
        n_bins = h.GetNbinsX()
        cat_config = self.get_active_category_config()
        do_blind = self.core_config['do_blind']
        blind_range = cat_config['dataset']['blind_range']
        for i in range(1, n_bins + 1):
            bin_center = h.GetBinCenter(i)
            # skip bins that are out of range
            if (bin_center > xmax) or (bin_center < xmin):
                continue
            # set bins to 0 in blind range
            if (do_blind and blind_range) and \
               (bin_center > blind_range[0]) and (bin_center < blind_range[1]):
                if h.GetBinContent(i) > 0:
                    h.SetBinContent(i, 0)
                continue
            x.setVal(bin_center)
            bin_content = h.GetBinContent(i)
            weight = max(bin_content * scale, self.EPSILON / 1000.)
            w.setVal(weight)
            dataset.add(ROOT.RooArgSet(x, w), weight)
        
    def release_ghost(self, dataset:ROOT.RooDataSet, datahist:ROOT.RooDataHist,
                      obs:ROOT.RooRealVar, weight_var:ROOT.RooRealVar, ghost_weight:float):
        do_blind = self.core_config['do_blind']
        cat_config = self.get_active_category_config()
        blind_range = cat_config['dataset']['blind_range']
        n_bins = datahist.GetNbinsX()
        for i in range(1, n_bins + 1):
            if datahist.GetBinContent(i) == 0:
                bin_center = datahist.GetBinCenter(i)
                if (do_blind and blind_range) and \
                   (bin_center > blind_range[0]) and (bin_center < blind_range[1]):
                    continue
                obs.setVal(bin_center)
                weight_var.setVal(ghost_weight)
                dataset.add(ROOT.RooArgSet(obs, weight_var), ghost_weight)
                # also put the ghost weight in the histograms
                datahist.SetBinContent(i, ghost_weight)
                
    def attach_constraints(self, ws:ROOT.RooWorkspace, constraints:ROOT.RooArgSet):
        category_name = self.current_category
        self.stdout.debug(f"REGTEST: Attaching contraint pdfs to workspace for the category {category_name}")
        sum_pdf_name = f"{self.KEYWORDS['sum_pdf_name']}_{category_name}"
        final_pdf_name = f"{self.KEYWORDS['final_pdf_name']}_{category_name}"
        remove_set = ROOT.RooArgSet()
        pdf = ws.pdf(sum_pdf_name)
        if not pdf:
            raise RuntimeError(f"sum pdf `{sum_pdf_name}` not defined")
        for constraint in constraints:
            constr_name = constraint.GetName()
            np_name = constr_name.replace(self.KEYWORDS['constrterm_prefix'], "")
            if not pdf.getVariables().find(np_name):
                self.stdout.warning(f"WARNING: constraint term {constr_name} with NP "
                                    f" {np_name} is redundant in the category {category_name}. "
                                    f"It will be removed...", "red")
                remove_set.add(constraint)
            else:
                self.import_object(ws, constraint)
        for constraint in remove_set:
            constraints.remove(constraint)
        pdf_components = [sum_pdf_name] + [constraint.GetName() for constraint in constraints]
        pdf_str = ",".join(pdf_components)
        model_expr = f"PROD::{final_pdf_name}({pdf_str})"
        self.import_expression(ws, model_expr)
        
    def get_correlated_terms(self, ws:ROOT.RooWorkspace, nuis:ROOT.RooArgSet) -> List[str]:
        correlated = []
        cat_config = self.get_active_category_config()
        poi_names = self.get_poi_names()
        correlate_items = cat_config['correlate_items']
        for poi_name in poi_names:
            correlate_items.append(poi_name)
        cat_config['correlate_items'] = remove_list_duplicates(correlate_items)
        for item in cat_config['correlate_items']:
            # does not exist
            if (not ws.obj(item)):
                continue
            if (not ws.var(item)):
                raise RuntimeError(f"correlated variable `{item}` is not properly implemented"
                                   f" as RooRealVar in the workspace")
            correlated.append(item)
        correlated += [np.GetName() for np in nuis]
        observable_name = cat_config['observable']['name']
        correlated.append(observable_name)
        return correlated
    
    def get_poi_names(self):
        return self.core_config['poi_names']
    
    def get_observable(self, ws:ROOT.RooWorkspace):
        cat_config = self.get_active_category_config()
        observable_name = cat_config['observable']['name']
        obs = ws.var(observable_name)
        if not obs:
            raise RuntimeError("observable not defined in the workspace")
        return obs

    def implement_blind_range(self, ws:ROOT.RooWorkspace):
        # range_name = "" : all blinded
        # range_name = None: no blinding
        # otherwise partially blinded
        cat_config = self.get_active_category_config()
        category_name = self.current_category
        observable_name = cat_config['observable']['name']
        observable_range = [cat_config['observable']['min'], cat_config['observable']['max']]
        obs = ws.var(observable_name)
        if not obs:
            raise RuntimeError("observable variable not initialized")        
        # now handle blinding if needed
        blind_range = cat_config['dataset']['blind_range']
        do_blind = self.core_config["do_blind"]
        if do_blind:
            if blind_range:
                self.stdout.info(f"REGTEST: Implement blind range [{blind_range[0]}, {blind_range[1]}]")
                sideband_lo_range_name = f"{self.KEYWORDS['sb_lo']}_{category_name}"
                sideband_hi_range_name = f"{self.KEYWORDS['sb_hi']}_{category_name}"
                blind_range_name = f"{self.KEYWORDS['blind']}_{category_name}"
                obs.setRange(sideband_lo_range_name, observable_range[0], blind_range[0])
                obs.setRange(blind_range_name, blind_range[0], blind_range[1])
                obs.setRange(sideband_hi_range_name, blind_range[1], observable_range[1])
                if (blind_range[0] == observable_range[0]) and \
                   (blind_range[1] == observable_range[1]):
                    self.stdout.info(f"REGTEST: Category `{category_name}` is fully blinded. "
                                     f"No side-band exists.")
                    cat_config['range_name'] = ""
                elif (blind_range[1] == observable_range[1]):
                    cat_config['range_name'] = sideband_lo_range_name
                elif (blind_range[0] == observable_range[0]):
                    cat_config['range_name'] = sideband_hi_range_name
                else:
                    cat_config['range_name'] = f"{sideband_lo_range_name},{sideband_hi_range_name}"
            else:
                cat_config['range_name'] = ""
        else:
            cat_config['range_name'] = None
        
    @staticmethod
    def _generate_expr(head:str, argset:ROOT.RooArgSet, close_expr:bool=True):
        tokens = [i.GetName() for i in argset]
        expr_str = head + ",".join(tokens)
        if close_expr:
            expr_str += ")"
            expr_str = expr_str.strip().replace(",)", ")")
        return expr_str
    
    def _fix_item_priority(self):
        cat_config = self.get_active_category_config()
        items_highpriority  = cat_config['items_highpriority']
        items_lowpriority   = cat_config['items_lowpriority']
        _items_highpriority = []
        for item in items_highpriority:
            if self._item_has_dependent(item, items_lowpriority):
                items_lowpriority.append(item)
            else:
                _items_highpriority.append(item)
        cat_config['items_highpriority'] = _items_highpriority
    
    def _item_has_dependent(self, expr:str, reference_list:List[str]):
        _, item_type = self._get_object_name_and_type_from_expr(expr)
        self.stdout.debug(f"REGTEST: item `{expr}` has type `{item_type}`")
        if item_type in ['variable', 'defined']:
            return False
        item_list = self._decompose_function_expr(expr)
        self.stdout.debug(f"REGTEST: Composition of high priority item {expr}: "
                          f"{', '.join(item_list)}")
        for this_name in item_list:
            for reference in reference_list:
                that_name, _ = self._get_object_name_and_type_from_expr(reference)
                if this_name == that_name:
                    return True
        return False

    @staticmethod
    def _decompose_function_expr(expr:str):
        start = expr.find("(")
        end = expr.rfind(")")
        if (start < 0) or (end < 0):
            raise RuntimeError(f"not a valid function expression `{expr}`")
        tokens = expr[start + 1 : end].split(",")
        if ("expr::" in expr) or ("EXPR::" in expr):
            tokens = tokens[1:]
        return tokens
        
    @staticmethod
    def _get_object_name_and_type_from_expr(expr:str):
        if ("::" in expr) and ("(" in expr):
            object_type = "function"
            object_name = expr.split("::")[1].split("(")[0]
        elif ("[" in expr):
            object_type = "variable"
            object_name = expr.split("[")[0]
        elif (":" in expr) and not ("::" in expr):
            raise RuntimeError(f"syntax error for the expression `{expr}`: missing colon pair")
        else:
            object_type = "defined"
            object_name = expr
        return object_name, object_type
            
    def import_uncert_expr(self, ws:ROOT.RooWorkspace, expr:str, var_name:str, prefix:str):
        if is_float(expr):
            new_expr = f"{prefix}{var_name}[{expr}]"
            return self.import_expression(ws, new_expr)
        else:
            return self.import_expression(ws, expr)

    def _translate_keyword(self, expr:str):
        category_name = self.current_category
        observable_name = self.cat_config[category_name]['observable']['name']
        expr = expr.replace(self.KEYWORDS['response'], 
                            self.KEYWORDS['response_prefix'] + \
                            self.KEYWORDS['shape'] + "_")
        expr = expr.replace(self.KEYWORDS['observable'],
                            observable_name)
        expr = expr.replace(self.KEYWORDS['category'],
                            category_name)
        expr = expr.replace(self.KEYWORDS['common'],
                            self.KEYWORDS['allproc'])
        expr = expr.replace(self.KEYWORDS['lt'], "<")
        expr = expr.replace(self.KEYWORDS['le'], "<=")
        expr = expr.replace(self.KEYWORDS['gt'], ">")
        expr = expr.replace(self.KEYWORDS['ge'], ">=")
        expr = expr.replace(self.KEYWORDS['and'], "%%")
        expr = expr.replace(self.KEYWORDS['or'], "||")
        return expr
       
    def _translate_node_attrib(self, node:Dict, attrib_name:str, process:str="",
                               required:bool=True, default:str=""):
        expr = self._get_node_attrib(node, attrib_name, required, default)
        expr = self._translate_keyword(expr)
        if (self.KEYWORDS['process'] in expr):
            if process == "":
                raise RuntimeError(f"process name not provided for the expression `{expr}`")
            expr = expr.replace(self.KEYWORDS['process'], f"_{process}")
        return expr
    
    def get_chain_and_branch(self, filename:str, treename:str, varname:str,
                             cut:str="", check_only:bool=False):
        chain = ROOT.TChain(treename)
        filenames = filename.split(",")
        filepaths = [self.get_relpath(filename) for filename in filenames]
        for filepath in filepaths:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"input data file `{filepath}` not found")
            status = chain.AddFile(filepath, -1)
            if not status:
                raise RuntimeErrro(f"cannot find TTree `{treename}` in data file `{filepath}`")
        if cut != "":
            chain = chain.CopyTree(cut)
        branch = chain.FindBranch(varname)
        if not branch:
            raise RuntimeError(f"cannot find TBranch `{varname}` in TTree `{treename}` "
                               f"in data file `{filename}`")
        if check_only:
            return Nones
        return chain, branch
    
    def get_histogram(self, filename:str, histname:str, check_only:bool=False):
        filepath = self.get_relpath(filename)
        if os.path.exists(filepath):
            raise FileNotFoundError(f"input data file `{filepath}` not found")
        f = ROOT.TFile(filepath)
        histname = data_config['histname']
        histogram = f.Get(histname)
        if not isinstance(histogram, ROOT.TH1):
            raise RuntimeError(f"no TH1 named `{histanme}` found in data file `{filepath}`")
        if check_only:
            return None
        histogram.SetDirectory(0)        
        return histogram
    
    def data_file_sanity_check(self):
        category_name = self.current_category
        category_type = self.cat_config[category_name]['category_type']
        data_config = self.cat_config[category_name]['dataset']
        filename = data_config['filename']    
        if category_type == self.KEYWORDS['counting']:
            if (filename != "") and (self.check_file_exist(filename)):
                raise FileNotFoundError(f"input data file `{filepath}` not found")
            if (filename == "") and (data_config.get("num_data", -1) < 0):
                raise RuntimeError("pleasee provide either a valid input data filename, or "
                                   "a valid number of data events for a counting experiment")
        else:
            if data_config['filetype'] != self.KEYWORDS['ascii']:
                if data_config['filetype'] == self.KEYWORDS['histogram']:
                    histname = data_config['histname']
                    self.get_histogram(fileame, histname, check_only=True)
                else:
                    treename = data_config['treename']
                    varname = data_config['varname']
                    self.get_chain_and_branch(filename, treename, varname, check_only=True)
    
    def fetch_node(self, nodes:List, tag:str, xml_filename:str, xml_type:str="channel", 
                   allow_missing:bool=False, allow_multiple:bool=False):
        target_node = [node for node in nodes if node['tag'] == tag]
        if (len(target_node) > 1) and (not allow_multiple):
            raise RuntimError(f"Multiple `{tag}` node found in {xml_type} XML file `{xml_filename}`")
        elif (len(target_node) == 0) and (not allow_missing):
            raise RuntimError(f"No `{tag}` node found in {xml_type} XML file `{xml_filename}`")
        elif (len(target_node) == 1) and (not allow_multiple):
            target_node = target_node[0]
        return target_node
    
    def get_active_category_config(self):
        category_name = self.current_category
        if category_name not in self.cat_config:
            raise RuntimeError(f"no config info found for the category `{category_name}`")
        cat_config = self.cat_config[category_name]
        return cat_config
        
    def read_systematics_node(self, node:Dict, domain:str):
        cat_config = self.get_active_category_config()
        syst_expr = self._get_node_attrib(node, "Name")
        self.stdout.debug(f"REGTEST: Reading systematic `{syst_expr}`")
        syst = Systematic()
        syst.name = self._translate_node_attrib(node, "Name", domain)
        # if the process of the systematic is specified, use the 
        # specified process. Otherwise use the default one
        syst.process = self._translate_node_attrib(node, "Process", domain, False, "")
        # common systematics
        if domain == self.KEYWORDS['allproc']:
            # if a process name is specified, use it as domain name and 
            # remove it from common systematic
            if syst.process != "":
                syst.domain = syst.process
            # otherwise consider it as common systematic
            else:
                # for systematics under a sample, the domain is always 
                # the sample name
                syst.domain = domain
        else:
            # for systematics under a sample, the domain is always
            # the sample name
            syst.domain = domain
            if syst.process == "":
                syst.process = domain
            # if the systematic has a process, attach it to domain name
            # as process name
            else:
                syst.process = f"{domain}_{syst.process}"
        syst.whereto = self._get_node_attrib(node, "WhereTo")
        syst.nominal = self._get_node_attrib(node, "CentralValue", dtype="float")
        syst.constr_term = self._get_node_attrib(node, "Constr")
        if (syst.nominal <= 0.) and \
        (syst.constr_term in [self.KEYWORDS['logn'], self.KEYWORDS['asym']]):
            raise RuntimeError(f"failed to parse systematic {syst.name}:"
                               f" constraint term {syst.constr_term} received"
                               f" negative central value ({syst.nominal})")
        uncert_expr = self._get_node_attrib(node, "Mag", dtype="str_list")
        uncert_val  = [float(v) if is_float(v) else None for v in uncert_expr]
        uncerts_sign = [-1 if (v is not None) and (v < 0) else +1 for v in uncert_val]
        beta = self._get_node_attrib(node, "Beta", False, "1", dtype="float")
        beta *= uncerts_sign[0]
        syst.beta = beta
        
        #assymetric uncertainties
        if len(uncert_expr) == 2:
            syst.errorhi = abs(uncert_val[0]) if (uncert_val[0] is not None) else uncert_expr[0]
            syst.errorlo = abs(uncert_val[1]) if (uncert_val[1] is not None) else uncert_expr[1]
            # a RooFit feature noticed by Jared:
            # if one uses FlexibleInterpVar to implement a systematic on a process,
            # then for the same systematic on a different process FlexibleInterpVar 
            # has to be used as well. Otherwise the code will crash.
            if syst.constr_term != self.KEYWORDS['asym']:
                if syst.errorhi != syst.errorlo:
                    self.stdout.info(f"INFO: Upper uncert. ({syst.errorhi}) and"
                                     f" lower uncert. ({syst.errorlo}) for"
                                     f" {syst.constr_term} systematic "
                                     f" {syst.name} are not identical. "
                                     f"Will treat as asymmetric uncertainty "
                                     f"using FlexibleInterpVar with "
                                     f"interpolation code 4. Next time "
                                     f"please use keyword {self.KEYWORDS['asym']} "
                                     f" for constraint term type instead of {syst.constr_term}.")
            syst.constr_term = self.KEYWORDS['asym']
        else:
            syst.errorhi = abs(uncert_val[0]) if uncert_val[0] is not None else uncert_expr[0]
            syst.errorlo = abs(uncert_val[0]) if uncert_val[0] is not None else uncert_expr[0]
        if syst.domain not in cat_config['systematics']:
            cat_config['systematics'][syst.domain] = []
        self.add_syst_object(syst)

    def add_syst_object(self, syst:Systematic):
        cat_config = self.get_active_category_config()
        syst_list = cat_config['systematics'][syst.domain]
        for _syst in syst_list:
            if _syst.is_equal(syst):
                raise RuntimeError(f"systematic `{syst.name}` applied on `{syst.whereto}` "
                                   f"is duplicated for the process `{syst.process}`")
        cat_config['systematics'][syst.domain].append(syst)        
        
    def add_sample_object(self, sample:Sample):
        cat_config = self.get_active_category_config()
        sample_list = cat_config['samples']
        for _sample in sample_list:
            if _sample.is_equal(sample):
                raise RuntimeError(f"duplicated sample `{sample.process}`")
        cat_config['samples'].append(sample)
        
    def read_item_node(self, node:Dict):
        cat_config = self.get_active_category_config()
        item = self._translate_node_attrib(node, "Name")
        if (self.KEYWORDS['response'] in item) or \
           (self.KEYWORDS['response_prefix'] in item):
            cat_config['items_lowpriority'].append(item)
        else:
            cat_config['items_highpriority'].append(item)
        
    def read_channel_import_node(self, node:Dict, ws:ROOT.RooWorkspace):
        filename = self._translate_node_attrib(node, "FileName")
        filepath = self.get_relpath(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"import XML file `{filepath}` not found")
        self.stdout.debug(f"REGTEST: Reading import XML file `{filepath}`")
        xml_data = self._xml_to_dict(filepath)
        nodes = xml_data['children']
        self.read_channel_xml_nodes(nodes, ws)
        
    def read_sample_import_node(self, node:Dict, sample:Sample):
        filename = self._translate_node_attrib(node, "FileName")
        filepath = self.get_relpath(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"import XML file `{filepath}` not found")
        self.stdout.info(f"REGTEST: Importing items for `{sample.process}` from {filepath}")
        xml_data = self._xml_to_dict(filepath)
        nodes = xml_data['children']
        self.read_sample_subnode(nodes, sample)
    
    def read_sample_factor_node(self, node:Dict, sample:Sample, factor_type:str):
        factor = self._translate_node_attrib(node, "Name", sample.process)
        if factor_type == "norm":
            sample.norm_factors.append(factor)
        elif factor_type == "shape":
            sample.shape_factors.append(factor)
        is_correlated = self._get_node_attrib(node, "Correlate", False, "0", dtype="int")
        if is_correlated:
            cat_config = self.get_active_category_config()
            item_name = self._get_object_name_and_type_from_expr(factor)
            cat_config['correlate_items'].append(item_name)
    
    def read_data_node(self, node:Dict, ws:ROOT.RooWorkspace):
        cat_config = self.get_active_category_config()
        # extract observable information
        observable_expr = self._translate_node_attrib(node, "Observable")
        observable_name = self.import_expression(ws, observable_expr)
        observable_min = ws.var(observable_name).getMin()
        observable_max = ws.var(observable_name).getMax()
        if observable_min >= observable_max:
            raise RuntimeError(f"invalid range for observable `{observable_name}`: "
                               f"min={observable_min}, max={observable_max}")        
        is_counting = cat_config['category_type'] == self.KEYWORDS['counting']
        if is_counting:
            observable_nbins = 1
        else:
            observable_nbins = int(self._get_node_attrib(node, "Binning"))
        ws.var(observable_name).setBins(observable_nbins)
        
        cat_config['observable'] = {
            'name': observable_name,
            'min': observable_min,
            'max': observable_max,
            'nbins': observable_nbins
        }
        
        data_filename = self._translate_node_attrib(node, "InputFile", "",
                                                    required=not is_counting,
                                                    default="")
        data_filetype = self._get_node_attrib(node, "FileType", False,
                                              self.KEYWORDS['ascii'])
        data_filetype = data_filetype.lower()
        data_config = {}
        data_config['filename'] = data_filename
        data_config['filetype'] = data_filetype
        if data_filetype != self.KEYWORDS['ascii']:
            # reading from ntuples/histogram
            if data_filetype == self.KEYWORDS['histogram']:
                data_config['histname'] = self._translate_node_attrib(node, "HistName")
            else:
                data_config['treename'] = self._translate_node_attrib(node, "TreeName")
                data_config['varname'] = self._translate_node_attrib(node, "VarName")
                data_config['cut'] = self._translate_node_attrib(node, "Cut", "",
                                                                 required=False,
                                                                 default="")
        inject_ghost = self._get_node_attrib(node, "InjectGhost", False, "0", dtype="int")
        data_config['inject_ghost'] = inject_ghost
        if (is_counting and data_filename == ""):
            data_config['num_data'] = self._get_node_attrib(node, "NumData")
        else:
            data_config['num_data'] = -1
        data_config['scale_data'] = self._get_node_attrib(node, "ScaleData", False, "1", dtype="float")
        blind_range = self._get_node_attrib(node, "BlindRange", False, None)
        if blind_range:
            blind_range = blind_range.split(",")
            if (len(blind_range) != 2) or (not is_float(blind_range[0])) or (not is_float(blind_range[1])):
                raise RuntimeError(f"invalid blind range format: {blind_range}")
            blind_range = [float(r) for r in blind_range]
            if (blind_range[1] <= blind_range[0]) or (blind_range[0] < observable_min) or (blind_range[1] > observable_max):
                raise RuntimeError(f"invalid blinding range provided: min={blind_range[0]}, max={blind_range[1]}")
        data_config['blind_range'] = blind_range
        cat_config['dataset'] = data_config
        
        self.data_file_sanity_check()
        
    def read_correlate_node(self, node:Optional[Dict]=None):
        cat_config = self.get_active_category_config()
        if node:
            item_str = node['text']
            if not item_str:
                filename = cat_config['input_file']
                raise RuntimeError(f"no items defined for correlation in channel XML file `{filename}`")
            correlate_items = item_str.split(",")
        else:
            correlate_items = []
        cat_config['correlate_items'] = correlate_items
        
    def read_sample_node(self, node:Dict):
        cat_config = self.get_active_category_config()
        is_counting = cat_config['category_type'] == self.KEYWORDS['counting']
        sample = Sample()
        sample.process = self._translate_node_attrib(node, "Name")
        sample.input_file = self._translate_node_attrib(node, "InputFile", sample.process,
                                                        required=not is_counting,
                                                        default="")
        syst_groups = self._translate_node_attrib(node, "ImportSyst", sample.process,
                                                  required=False, default=self.KEYWORDS['self'])
        syst_groups = [s for s in syst_groups.split(",") if s != sample.process]
        syst_groups = remove_list_duplicates(syst_groups)
        sample.syst_groups = syst_groups
        
        if cat_config['luminosity'] > 0:
            is_multiply_lumi = self._get_node_attrib(node, "MultiplyLumi", False, "1", dtype="int")
        else:
            is_multiply_lumi = 0
        
        # assemble the yield central value
        if is_multiply_lumi:
            sample.norm_factors.append(self.KEYWORDS['lumi_name'])        
        
        norm_factor_names = {
            'norm': 'Norm',
            'xs': 'XSection',
            'br': 'BR',
            'efficiency': 'SelectionEff',
            'acceptance': 'Acceptance',
            'correction': 'Correction'
        }
        
        for key, name in norm_factor_names.items():
            norm_value = self._translate_node_attrib(node, name, sample.process,
                                                     required=False, default="")
            if norm_value != "":
                norm_name = self.KEYWORDS[f'{key}_name']
                sample.norm_factors.append(f"{norm_name}_{sample.process}[{norm_value}]")
                
        sample.share_pdf_group = self._translate_node_attrib(node, "SharePdf", sample.process,
                                                             required=False, default="")
        subnodes = node['children']
        self.stdout.debug(f"REGTEST: Reading sample `{sample.process}`")
        self.read_sample_subnode(subnodes, sample)
        self.add_sample_object(sample)
        
    def read_sample_subnode(self, nodes:List, sample:Sample):
        for node in nodes:
            name = node['tag']
            if name == "Systematic":
                self.read_systematics_node(node, sample.process)
            elif name == "NormFactor":
                self.read_sample_factor_node(node, sample, "norm")
            elif name == "ShapeFactor":
                self.read_sample_factor_node(node, sample, "shape")
            elif name == "ImportItems":
                self.read_sample_import_node(node, sample)
            else:
                raise RuntimeError(f"unsupported node `{name}`")        
    
    def read_channel_xml_nodes(self, nodes:List, ws:ROOT.RooWorkspace):
        for node in nodes:
            name = node['tag']
            if name == "Item":
                self.read_item_node(node)
            elif name == "Systematic":
                self.read_systematics_node(node, self.KEYWORDS['allproc'])
            elif name == "Sample":
                self.read_sample_node(node)
            elif name == "ImportItems":
                self.read_channel_import_node(node, ws)
            else:
                raise RuntimeError(f"unsupported node `{name}`")
    def make_np(self, ws:ROOT.RooWorkspace, syst:Systematic, nuis:ROOT.RooArgSet,
                constraint:ROOT.RooArgSet, globobs:ROOT.RooArgSet, expected:ROOT.RooArgSet):
        var_name = f"{syst.whereto}_{syst.name}"
        if syst.domain != self.KEYWORDS['allproc']:
            var_name += f"_{syst.process}"
        glob_name = self.KEYWORDS['globalobs_prefix'] + syst.name
        constr_name = self.KEYWORDS['constrterm_prefix'] + syst.name
        response_name = self.KEYWORDS['response_prefix'] + var_name
        
        if syst.constr_term == self.KEYWORDS['asym']:
            self.stdout.debug(f"REGTEST: Set up nuisance parameter {syst.name} as asymmetric uncertainty "
                              f"on the process {syst.process}")
            nuis_var = ROOT.RooRealVar(syst.name, syst.name, 0, -5, 5)
            beta_name = f"beta_{var_name}"
            beta_var = ROOT.RooRealVar(beta_name, beta_name, syst.beta)
            nuis_times_beta_name = f"{var_name}_times_beta"
            nuis_times_beta = ROOT.RooProduct(nuis_times_beta_name, nuis_times_beta_name, 
                                              ROOT.RooArgSet(nuis_var, beta_var))
            nuis_list = ROOT.RooArgList(nuis_times_beta)
            code = np.array([4])
            if (not isinstance(syst.errorhi, str)) and (not isinstance(syst.errorlo, str)):
                # both upper and lower uncertainties are numbers, can simply use FlexibleInterpVar
                sigma_var_high = np.array([syst.nominal + syst.errorhi])
                sigma_var_low = np.array([syst.nominal / (syst.nominal + syst.errorlo)])
                expected_var = ROOT.RooStats.HistFactory.FlexibleInterpVar(response_name, response_name,
                                                                           nuis_list, syst.nominal,
                                                                           sigma_var_low, sigma_var_high, code)
                self.import_object(ws, expected_var)
            else:
                # need to use FlexibleInterpVarMkII
                nominal_expr = self.import_uncert_expr(ws, f"nominal_{var_name}[{syst.nominal}]")
                uncert_hi_name = self.import_uncert_expr(ws, syst.errorhi, var_name, self.KEYWORDS['uncert_hi_prefix'])
                uncert_lo_name = self.import_uncert_expr(ws, syst.errorlo, var_name, self.KEYWORDS['uncert_lo_prefix'])
                varhi_expr = f"expr::{self.KEYWORDS['variationhi_prefix']}{var_name}('@0+@1', {nominal_expr}, {uncert_hi_name})"
                varlo_expr = f"expr::{self.KEYWORDS['variationlo_prefix']}{var_name}('@0/(@0+@1)', {nominal_expr}, {uncert_lo_name})"
                variation_hi_name = self.import_expression(ws, varhi_expr)
                variation_lo_name = self.import_expression(ws, varlo_expr)
                sigma_expr_high = ROOT.RooArgList()
                sigma_expr_low = ROOT.RooArgList()
                sigma_expr_high.add(ws.arg(variation_hi_name))
                sigma_expr_low.add(ws.arg(variation_lo_name))
                expected_var = ROOT.FlexibleInterpVarMkII(response_name, response_name, nuis_list, syst.nominal,
                                                          sigma_expr_low, sigma_expr_high, code)
                self.import_object(ws, expected_var)
        else:
            nominal_expr = self.import_expression(ws, f"nominal_{var_name}[{syst.nominal}]")
            np_name = self.import_expression(ws, f"{syst.name}[0, -5, 5]", True)
            _buffer = f"prod::{var_name}_times_beta({syst.name}, beta_{var_name}[{syst.beta}])"
            nuis_times_beta_expr = self.import_expression(ws, _buffer)
            uncert_name = self.import_uncert_expr(ws, syst.errorhi, var_name, self.KEYWORDS['uncert_sym_prefix'])
            self.stdout.debug(f"REGTEST: Set up nuisance parameter {syst.name} as {syst.constr_term} "
                              f"uncertainty on process {syst.process}")
            if (syst.constr_term in [self.KEYWORDS['gaussian'], self.KEYWORDS['dfd']]):
                # the reason we need to keep plain implementation for Gaussian uncertainty is mainly due to spurious signal.
                # if we use FlexibleInterpVar, the response will be truncated at 0, but we need the response to go negative.
                uncert_wrapper_expr = f"prod::uncert_{syst.constr_term}_{var_name}({nuis_times_beta_expr}, {uncert_name})"
                expected_expr = f"sum::{response_name}({nominal_expr}, {uncert_wrapper_expr})"
                self.import_expression(ws, expected_expr)
            elif (syst.constr_term == self.KEYWORDS['logn']):
                log_kappa_expr = f"expr::log_kappa_{var_name}('log(1+@0/@1)', {uncert_name}, {nominal_expr})"
                uncert_wrapper_expr = f"expr::uncert_{syst.constr_term}_{var_name}('exp(@0*@1)', " +\
                                      f"{nuis_times_beta_expr}, {log_kappa_expr})"
                expected_expr = f"prod::{response_name}({uncert_wrapper_expr}, {nominal_expr})"
                self.import_expression(ws, expected_expr)
            else:
                raise RuntimeError(f"unknown constraint type {syst.constr_term} for NP {syst.name} "
                                   f"in process {syst.process}. Available choices: "
                                   f"{self.KEYWORDS['logn']} (lognormal), "
                                   f"{self.KEYWORDS['gaussian']} (gaussian), "
                                   f"{self.KEYWORDS['asym']} (asymmetric), "
                                   f"{self.KEYWORDS['dfd']} (double-fermi-dirac) ")
        if syst.constr_term == self.KEYWORDS['dfd']:
            self.stdout.debug(f"REGTEST: Creating DFD constraint term for NP {syst.name}")
            self.import_expression(ws, f"EXPR::{constr_name}('1/((1+exp(@2*(@0-@3-@1)))*(1+exp(-1*@2*"
                               f"(@0-@3+@1))))', {syst.name}, DFD_e[1], DFD_w[500], {glob_name}[0,-5,5])", True)
        else:
            self.stdout.debug(f"REGTEST: Creating RooGaussian constraint term for NP {syst.name}")
            self.import_expression(ws, f"RooGaussian::{constr_name}({syst.name}, {glob_name}[0,-5,5],1)", True)
        nuis.add(ws.var(syst.name), True)
        constraint.add(ws.pdf(constr_name), True)
        globobs.add(ws.var(glob_name), True)
        expected.add(ws.function(response_name), True)
        self.stdout.debug(f"REGTEST: Finished implementing systematic {syst.name}")
    
    def get_model(self, ws:ROOT.RooWorkspace, sample:Sample, nuis:ROOT.RooArgSet,
                  constraints:ROOT.RooArgSet, globobs:ROOT.RooArgSet):
        self.stdout.debug("REGTEST: Getting model")
        tag_name = sample.get_tag_name()
        sample.model_name = self.KEYWORDS['pdf_prefix'] + tag_name
        
        if ws.pdf(sample.model_name):
            if is_shared_pdf:
                # use shared pdf
                self.stdout.debug(f"REGTEST: PDF {sample.model_name} has been created in the workpace.")
                return None
            else:
                raise RuntimeError(f"PDF {sample.model_name} already exists but the user asks to create it again")
        self.stdout.debug(sample.model_name)
        cat_config = self.get_active_category_config()
        is_counting = cat_config['category_type'] == self.KEYWORDS['counting']
        obs_name = cat_config['observable']['name']
        if is_counting:
            # in counting experiment we only need a uniform pdf
            self.import_expression(ws, f"RooUniform::{sample.model_name}({obs_name})")
        else:
            filename = sample.input_file            
            self.read_model_xml(filename, ws, sample, nuis, constraints, globobs)
            
    def read_model_xml(self, filename:str, ws:ROOT.RooWorkspace, sample:Sample,
                      nuis:ROOT.RooArgSet, constraints:ROOT.RooArgSet, globobs:ROOT.RooArgSet):
        filepath = self.get_relpath(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"model xml file `{filepath}` not found")
        root_node = self._xml_to_dict(filepath)
        
        model_type = self._get_node_attrib(root_node, "Type").lower()
        if model_type == self.KEYWORDS['userdef']:
            self.stdout.debug(f"REGTEST: Creating user-defined pdf from `{filepath}`")
            self.build_userdef_model(root_node, ws, sample)
        elif model_type == self.KEYWORDS['external']:
            self.build_external_model(root_node, ws, sample, nuis, constraints, globobs)
        elif model_type == self.KEYWORDS['histogram']:
            self.build_histogram_model(root_node, ws, sample)
        else:
            raise RuntimeError(f"unknown model type: {model_type} . Available choice: "
                               f" {self.KEYWORDS['userdef']}, {self.KEYWORDS['external']}, "
                               f" {self.KEYWORDS['histogram']}")
    
    def build_userdef_model(self, root_node:Dict, ws:ROOT.RooWorkspace, sample:Sample):
        cat_config = self.get_active_category_config()
        tag_name = sample.get_tag_name()
        obs_name = cat_config['observable']['name']
        cache_binning = self._get_node_attrib(root_node, "CacheBinning", False, "-1", dtype="int")
        obs = ws.var(obs_name)
        if cache_binning > 0:
            if not obs:
                raise RuntimeError("observable not initialized")
            # for the accuracy of Fourier transformation
            obs.setBins(cache_binning, "cache")
        is_success = False
        nodes = root_node['children']
        for node in nodes:
            name = node['tag']
            self.stdout.debug(f"REGTEST: Reading node `{name}`")
            if name == "Item":
                expr = self._translate_node_attrib(node, "Name", tag_name)
                self.import_expression(ws, expr)
            elif name == "ModelItem":
                factory_str = self._translate_node_attrib(node, "Name", tag_name)
                str_start = factory_str.find("::")+2
                str_end   = factory_str.find("(")
                pdf_name = factory_str[str_start:str_end]
                factory_str = factory_str[:str_start] + sample.model_name + factory_str[str_end:]
                self.import_expression(ws, factory_str)
                is_success = True
                break
            else:
                raise RuntimeError(f"unknown node `{name}`")
        if not is_success:
            raise RuntimeError("missing node `ModelItem` from model xml")
    
    def build_external_model(self, root_node:Dict, ws:ROOT.RooWorkspace, sample:Sample,
                             nuis:ROOT.RooArgSet, constraints:ROOT.RooArgSet, globobs:ROOT.RooArgSet):
        cat_config = self.get_active_category_config()
        _observable_name = cat_config['observable']['name']
        filename = self._translate_node_attrib(root_node, "Input")
        filepath = self.get_relpath(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"input file `{filepath}` not found")
        ws_name = self._translate_node_attrib(root_node, "WSName")
        model_name = self._translate_node_attrib(root_node, "ModelName")
        observable_name = self._translate_node_attrib(root_node, "ObservableName")
        tag_name = sample.get_tag_name()
        nodes = root_node['children']
        np_list, glob_list, constr_list = [], [], []
        self.stdout.debug(f"REGTEST: Use existing PDF `{model_name}` from the workspace `{filename}`")
        
        f_ext = ROOT.TFile(filename)
        ws_ext = f_ext.Get(ws_name)
        pdf_ext = ws_ext.function(model_name)
        
        name_maps = {}
        do_not_touch = [observable_name]
        
        for node in nodes:
            name = node['tag']
            if name == "Item":
                expr = self._translate_node_attrib(node, "Name", tag_name)
                self.import_object(ws, expr)
            elif name == "Fix":
                var_name = self._translate_node_attrib(node, "Name")
                var = ws_ext.var(var_name)
                if not var:
                    raise RuntimeError(f"no variable named `{var_name}` found im the workspace `{filepath}`")
                var.setConstant(1)
                var_val = self._get_node_attrib(node, "Value", False, "")
                if var_val != "":
                    var.setVal(float(var))
                self.stdout.debug(f"REGTEST: Fixed variable `{var_name}` at `{var.getVal()}")
            elif name == "Rename":
                # rename the object names in the input workspace
                old_name = self._translate_node_attrib(node, "OldName", tag_name)
                new_name = self._translate_node_attrib(node, "NewName", tag_name)
                do_not_touch.append(old_name)
                name_maps[old_name] = new_name
            elif name == "ExtSyst":
                # adding external systematics
                np_name = self._translate_node_attrib(node, "NPName")
                glob_name = self._translate_node_attrib(node, "GOName", "", False, "")
                constr_name = self._translate_node_attrib(node, "ConstrName", "",
                                                          required=glob_name!="", default="")
                np_list.append(np_name)
                glob_list.append(glob_name)
                constr_list.append(constr_name)
                do_not_touch.append(np_name)
            else:
                raise RuntimeError(f"unknown node `{name}`")
        # remove duplicated variables
        do_not_touch = ",".join(remove_list_duplicates(do_not_touch))
    
        # rename everything in the model by adding a tag to it
        ws_temp = ROOT.RooWorkspace("ws_temp")
        self.import_object(ws, pdf_ext, ROOT.RooFit.RenameAllNodes(tag_name),
                           ROOT.RooFit.RenameAllVariablesExcept(tag_name, do_not_touch))
        #ws_temp.importClassCode()
        if self.debug_mode:
            ws_temp.Print()
            
        pdf = ws_temp.function(f"{model_name}_{tag_name}")
        obs_ext = ws_temp.var(observable_name)
        if not obs_ext:
            raise RuntimeError(f"observable `{observable_name}` not found in the workspace `{filepath}`")
        if not isinstance(pdf, ROOT.RooAbsPdf):
            self.stdout.warning(f"WARNING: The object {model_name} is not a p.d.f as seen from RoOFit")
            self.stdout.warning("REGTEST: Constructing RooRealSumPdf for the pdf from histFactory")
            dummy_pdf = ROOT.RooUniform(f"{sample.model_name}_dummpy_pdf", "for RooRealSumPdf construction",
                                        obs_ext)
            frac = ROOT.RooRealVar(f"{sample.model_name}_real_pdf_frac", "for RooRealSumPdf construction", 1)
            pdf = ROOT.RooRealSumPdf(sample.model_name, "from histFactory", ROOT.RooArgList(pdf, dummy_pdf),
                                     ROOT.RooArgList(frac))
        else:
            name_maps[pdf.GetName()] = sample.model_name
        
        # rename observable (this step should never happen for a HistFactory workspace)
        if observable_name != _observable_name:
            name_maps[observable_name] = _observable_name
        self.stdout.info("REGTEST: The following variables will be renamed:")
        old_str = ",".join(name_maps.keys())
        new_str = ",".join(name_maps.values())
        self.stdout.info(f"REGTEST: Old: {old_str}")
        self.stdout.info(f"REGTEST: New: {new_str}")
        
        self.import_object(ws, pdf, ROOT.RooFit.RenameVariable(old_str, new_str),
                           ROOT.RooFit.RecycleConflictNodes())
        # import constraint terms
        for np_name, glob_name, constr_name in zip(np_list, glob_list, constr_list):
            new_np_name = np_name
            # check wheterh NP has been renamed. If yes, update the NP name
            for old_name, new_name in name_maps.items():
                if np_name == old_name:
                    new_np_name == new_name
                    break
            if glob_name != "":
                if (not ws_ext.var(np_name)) or (not ws_ext.var(glob_name)) or (not ws_ext.pdf(constr_name)):
                    raise RuntimeError(f"constraint pdf {constr_name} with NP = {np_name} and "
                                       f"GlobObs = {glob_name} does not exist")
                new_constr_name = self.KEYWORDS['constrterm_prefix'] + new_np_name
                new_glob_name = self.KEYWORDS['globalobs_prefix'] + new_np_name
                constr_pdf = ws_ext.pdf(constr_name)
                old_str = ",".join([constr_name, glob_name, np_name])
                new_str = ",".join([new_constr_name, new_glob_name, new_np_name])
                self.import_object(ws, constr_pdf, 
                                   ROOT.RooFit.RenameVariable(old_str, new_str))
                self.stdout.debug(f"REGTEST: Import systematics {new_np_name} "
                                  f"with constraint term {new_constr_name}")
                constraints.add(ws.pdf(new_constr_name), True)
                globobs.add(ws.var(new_glob_name), True)
            ws.var(new_np_name).setConstant(False)
            nuis.add(ws.var(new_np_name), True)
    
    def build_histogram_model(self, root_node:Dict, ws:ROOT.RooWorkspace, sample:Sample):
        cat_config = self.get_active_category_config()
        obs_name = cat_config['observable']['name']
        filename = self._translate_node_attrib(root_node, "Input")
        filepath = self.get_relpath(filename)
        histname = self._translate_node_attrib(root_node, "ModelName")
        rebin = self._get_node_attrib(root_node, "Rebin", False, "-1", dtype="int")
        self.stdout.debug(f"REGTEST: Creating histogram pdf from `{filepath}`")
        h = self.get_histogram(filename, histname)
        if rebin > 0:
            h.Rebin(rebin)
        obs = w.var(obs_name)
        if not obs:
            raise RuntimeError("observable not initialized")
        h_data = ROOT.RooDataHist("hdata", "hdata", obs, h)
        h_pdf = ROOT.RooHistPdf(sample.model_name, sample.model_name, obs, h_data)
        self.import_object(ws, h_pdf)
    
    def check_nuisance_parameters(self, model:ROOT.RooAbsPdf, nuis:ROOT.RooArgSet):
        cat_config = self.get_active_category_config()
        obs_name = cat_config['observable']['name']        
        var_set = model.getVariables()
        float_set = ROOT.RooArgSet()
        for var in var_set:
            if (not var.isConstant()):
                if var.getMin() == var.getMax():
                    var_name = var.GetName()
                    self.stdout.info(f"REGTEST: Fixing {var_name} to constant as it has same upper and loer boundary")
                    var.setConstant(True)
                else:
                    float_set.add(var)
        poi_obs_names = self.core_config['poi_names'] + [obs_name]
        # reove POI and observable from float set
        for name in poi_obs_names:
            float_var = float_set.find(name)
            if float_var:
                float_set.remove(float_var)
        num_np = len(nuis)
        num_poi = len(self.core_config['poi_names'])
        for var in float_set:
            if not nuis.find(var):
                nuis.add(var)
                var_name = var.GetName()
                self.stdout.info(f"REGTEST: Adding {var_name} to the nuisance parameter set")

        num_float = len(float_set)
        if num_float < num_np:
            self.stdout.warning(f"WARNING: There supposed to be {num_poi + num_np} free parameters, "
                                f"but only seen {num_float} in the category {self.current_category}. "
                                f"This is in principle not an issue, but please make sure you "
                                f"understand what you are doing")
            if self.debug_mode:
                self.stdout.debug("REGTEST: All free parameters: ")
                float_set.Print()
                self.stdout.debug("REGTEST: All nuisance parameters: ")
                nuis.Print()
        else:
            self.stdout.info("REGTEST: Number of nuisance parameters looks good!")