###############################################################################
### This is a reimplementation of workspaceCombiner library in python
### original author: Hongtao Yang
###############################################################################
import os
import re
import json
import time
from typing import Optional, Union, List, Dict

import numpy as np

import ROOT

import quickstats
from quickstats import semistaticmethod
from quickstats.components import AbstractObject, ExtendedModel
from quickstats.utils.io import Verbosity
from quickstats.utils.root_utils import load_macro, get_macro_dir
from quickstats.utils.common_utils import format_delimiter_enclosed_text
from quickstats.maths.numerics import is_float, pretty_value
from quickstats.components.basics import WSVariables
from quickstats.components.workspaces import XMLWSBase, WSObjectType, AsimovHandler

from quickstats.utils.enums import GeneralEnum

class ModifierAction(GeneralEnum):
    NORMAL     = 0
    CONSTRAINT = 1
    
class XMLWSModifier(XMLWSBase):
    
    def __init__(self, source:Union[str, Dict], basedir:Optional[str]=None,
                 minimizer_config:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(source=source, basedir=basedir, verbosity=verbosity)
        self.minimizer_config = minimizer_config
        self.load_extension()
        self.initialize(source=source)
        
    def initialize(self, source:Union[str, Dict]):
        self.config = None
        self.actions = {
            'map': [],
            'define': [],
            'redefine': [],
            'asimov': [],
            'constraint': [],
            'add_product_terms': {},            
        }
        self.actions['rename'] = {
            'workspace'   : {},
            'model_config': {},
            'dataset'     : {},
            'variable'    : {}
        }
        if isinstance(source, str):
            ext = os.path.splitext(source)[-1]
            if ext == ".xml":
                self.parse_config_xml(source)
            elif ext == ".json":
                self.parse_config_json(source)
            else:
                raise ValueError(f"unsupported file format: {ext}")
        elif isinstance(source, dict):
            self.parse_config_dict(source)
        else:
            raise ValueError(f"invalid input format: {source}")
        if len(self.actions['add_product_terms']) > 0:
            if (quickstats.root_version < (6, 26, 0)):
                raise RuntimeError("\"add product terms\" is only supported after ROOT 6.26")
            
    def parse_config_dict(self, source:str):
        _actions = source.pop("actions", {})
        config = {
            "input_file"         : source.pop("input_file"),
            "output_file"        : source.pop("output_file"),
            "model_name"         : source.pop("model_name", None),
            "workspace_name"     : source.pop("workspace_name", None),
            "model_config_name"  : source.pop("model_config_name", None),
            "data_name"          : source.pop("data_name", "combData"),
            "poi_names"          : source.pop("poi_names", None),
            "snapshot_nuis"      : source.pop("snapshot_nuis", []),
            "snapshot_globs"     : source.pop("snapshot_globs", []),
            "snapshot_pois"      : source.pop("snapshot_pois", []),
            "snapshot_all"       : source.pop("snapshot_all", []),
            "fix_parameters"     : source.pop("fix_parameters", None),
            "profile_parameters" : source.pop("profile_parameters", None),
            "strict"             : source.pop("strict", True)
        }
        if source:
            unknown_attributes = list(source)
            self.stdout.warning(f"WARNING: Unknown attributes received: {', '.join(unknown_attributes)}. "
                                "Ignoring...")
        actions = {
            "map"        : _actions.pop("map", []),
            "define"     : _actions.pop("define", []),
            "redefine"   : _actions.pop("redefine", []),
            "asimov"     : _actions.pop("asimov", []),
            "constraint" : [],
            "add_product_terms": _actions.pop("add_product_terms", {})
        }
        
        # handle constraint definition
        constraints = _actions.pop("constraint", [])
        for constraint_dict in constraints:
            constraint_node = {
                'attrib': constraint_dict
            }
            expr = self._get_node_attrib(constraint_node, "Name", required=True)
            constr_expr = self.parse_constr_expression(expr, constraint_node)
            if constr_expr['file'] is None:
                actions['define'].append(expr)
            actions['constraint'].append(constr_expr)

        _rename = _actions.pop("rename", {})
        rename = {
            "workspace"    : _rename.pop("workspace", {}),
            "model_config" : _rename.pop("model_config", {}),
            "dataset"      : _rename.pop("dataset", {}),
            "variable"     : _rename.pop("variable", {})
        }
        actions["rename"] = rename
        if _actions:
            unknown_attributes = list(_actions)
            self.stdout.warning(f"WARNING: Unknown action type: {', '.join(unknown_attributes)}. "
                                "Ignoring...")
        if _rename:
            unknown_attributes = list(_rename)
            self.stdout.warning(f"WARNING: Unknown object type in rename: {', '.join(unknown_attributes)}. "
                                "Ignoring...")
        
        self.config = config
        self.actions = actions
    
    def parse_config_json(self, filename:str):
        with open(filename, 'r') as f:
            source = json.load(f)
        self.parse_config_dict(source)
    
    def parse_config_xml(self, filename:str):
        root = self._xml_to_dict(filename)
        config = {
            'input_file'       : self._get_node_attrib(root, "InFile", required=True),
            'output_file'      : self._get_node_attrib(root, "OutFile", required=True),
            'model_name'       : self._get_node_attrib(root, "ModelName", required=False),
            'workspace_name'   : self._get_node_attrib(root, "WorkspaceName", required=False),
            'model_config_name': self._get_node_attrib(root, "ModelConfigName", required=False),
            'data_name'        : self._get_node_attrib(root, "DataName", required=False, default="combData"),
            'poi_names'        : self._get_node_attrib(root, "POINames", required=False, dtype="str_list"),
            'snapshot_nuis'    : self._get_node_attrib(root, "SnapshotNP", required=False, default=[], dtype="str_list"),
            'snapshot_globs'   : self._get_node_attrib(root, "SnapshotGO", required=False, default=[], dtype="str_list"),
            'snapshot_pois'    : self._get_node_attrib(root, "SnapshotPOI", required=False, default=[], dtype="str_list"),
            'snapshot_all'     : self._get_node_attrib(root, "SnapshotAll", required=False, default=[], dtype="str_list"),
            "fix_parameters"     : self._get_node_attrib(root, "FixParameters", required=False, default=None),
            "profile_parameters" : self._get_node_attrib(root, "ProfileParameters", required=False, default=None),
            'strict'           : self._get_node_attrib(root, "Strict", required=False, default="true", dtype="bool")
        }
        # for compatibility with older version of workspaceCombiner
        if config['workspace_name'] == "dummy":
            config['workspace_name'] = None
        if config['model_config_name'] == "dummy":
            config['model_config_name'] = None
        self.config = config
        
        # parse child nodes
        nodes = root['children']
        for node in nodes:
            self.parse_action_node(node)
            
    def parse_action_node(self, node:Dict):
        tag = node['tag']
        if tag == "Item":
            expr        = self._get_node_attrib(node, "Name", required=True)
            action_type = self._get_node_attrib(node, "Type", required=False,
                                                default=ModifierAction.NORMAL)
            action_type = ModifierAction.parse(action_type)
            if action_type == ModifierAction.CONSTRAINT:
                constr_expr = self.parse_constr_expression(expr, node)
                # define pdf that is not imported externally
                if constr_expr['file'] is None:
                    self.actions['define'].append(expr)
                self.actions['constraint'].append(constr_expr)
            else:
                self.actions['define'].append(expr)
        elif tag == "Map":
            expr = self._get_node_attrib(node, "Name", required=True)
            self.actions['map'].append(expr)
        elif tag == "Asimov":
            definitions = node['attrib']
            self.actions['asimov'].append(definitions)
        elif tag == "Rename":
            subnodes = node['child']
            for subnode in subnodes:
                self.parse_rename_node(subnode)
        elif tag == "AddProductTerm":
            name = self._get_node_attrib(node, "Name", required=True)
            extra_terms = self._get_node_attrib(node, "Terms", required=True, dtype="str_list")
            if name in self.actions['add_product_terms']:
                raise ValueError("AddProductTerm action defined multiple times for the variable "
                                 f"\"{name}\"")
            self.actions['add_product_terms'][name] = extra_terms
        else:
            raise RuntimeError(f"unknown item `{tag}`")
    
    def parse_rename_node(self, node:Dict):
        tag = node['tag']
        new_name = self._get_node_attrib(node, "New", required=True)
        if tag == 'Workspace':
            old_name_required = False
            target = 'workspace'
        elif tag == 'ModelConfig':
            old_name_required = False
            target = 'model_config'
        elif tag == 'Dataset':
            old_name_required = True
            target = 'dataset'
        elif tag == 'Variable':
            old_name_required = True
            target = 'variable'
        else:
            raise RuntimeError(f"unknown item `{tag}`")
        old_name = self._get_node_attrib(node, "Old", required=old_name_required)
        if old_name in self.actions['rename'][target]:
            raise RuntimeError(f"the {target.replace('_','')} \"{old_name}\" is renamed more than once")
        self.actions['rename'][target][old_name] = new_name
    
    def parse_constr_expression(self, expr:str, node:Dict):
        pdf_name, _ = self._get_object_name_and_type_from_expr(expr)
        nuis_name = self._get_node_attrib(node, "NP", required=False, default=[], dtype="str_list")
        glob_name = self._get_node_attrib(node, "GO", required=False, default=[], dtype="str_list")
        filename  = self._get_node_attrib(node, "FileName", required=False)
        result = {
            'pdf': pdf_name,
            'nuis': nuis_name,
            'glob': glob_name,
            'file': filename
        }
        return result
        
    @staticmethod
    def _get_object_name_and_type_from_expr(expr:str):
        if ("::" in expr) and ("(" in expr):
            object_type = WSObjectType.FUNCTION
            object_name = expr.split("::")[1].split("(")[0]
        elif ("(" in expr):
            object_type = WSObjectType.CONSTRAINT
            object_name = expr.split("(")[0]
        elif ("[" in expr):
            object_type = WSObjectType.VARIABLE
            object_name = expr.split("[")[0]
        elif (":" in expr) and not ("::" in expr):
            raise RuntimeError(f"syntax error for the expression `{expr}`: missing colon pair")
        else:
            object_type = WSObjectType.DEFINED
            object_name = expr
        return object_name, object_type
    
    def sanity_check(self):
        if self.config is None:
            raise RuntimeError("core configuration not set")
        if len(self.actions['rename']['workspace']) > 1:
            raise RuntimeError("workspace is renamed more than once")
        if len(self.actions['rename']['model_config']) > 1:
            raise RuntimeError("model config is renamed more than once")
    
    def create_modified_workspace(self):
        self.sanity_check()
        filename = self.config['input_file']
        ws_name  = self.config['workspace_name']
        mc_name  = self.config['model_config_name']
        self.stdout.info(f"INFO: Begin modification of the workspace \"{filename}\".")
        model    = ExtendedModel(filename, ws_name=ws_name, mc_name=mc_name,
                                 data_name=None, verbosity="WARNING")
        ws_orig  = model.workspace
        mc_orig  = model.model_config
        ws_name  = ws_orig.GetName()
        mc_name  = mc_orig.GetName()
        
        # create temporary workspace
        ws_tmp = ROOT.RooWorkspace(ws_name)
    
        title_str = format_delimiter_enclosed_text("Step 1: Redefine objects", "-")
        self.stdout.info(title_str)
        flag = self.redefine_objects(ws_orig, ws_tmp)
        # nothing is done
        if not flag:
            self.stdout.info("INFO: No objects are redefined.")
        
        title_str = format_delimiter_enclosed_text("Step 2: Create new objects", "-")
        self.stdout.info(title_str)
        flag = self.implement_external_pdfs(ws_tmp)
        flag |= self.implement_objects(ws_tmp)
        # nothing is done
        if not flag:
            self.stdout.info("INFO: No objects are defined.")
            
        # need to import datasets first so the variables are also imported into the workspace
        self.import_datasets(ws_orig, ws_tmp)
        
        title_str = format_delimiter_enclosed_text("Step 3: Rename variables", "-")
        self.stdout.info(title_str)
        rename_map = self.get_rename_map(ws_orig, ws_tmp)
        actual_rename_map = self.get_actual_rename_map(rename_map, ws_orig, ws_tmp)
        self.rename_variables(mc_orig, ws_tmp, rename_map)
        if not rename_map:
            self.stdout.info("INFO: No variables are renamed.")
        
        title_str = format_delimiter_enclosed_text("Step 4: Making output workspace", "-")
        self.stdout.info(title_str)

        # create final workspace
        if len(self.actions['constraint']) > 0:
            ws_final = ROOT.RooWorkspace(ws_name)
            sim_pdf = self.remake_simultaneous_pdf(mc_orig, ws_tmp)
            self.import_object(ws_final, sim_pdf)
            self.import_datasets(ws_orig, ws_final)
        else:
            ws_final = ws_tmp        
            
        # post processing pdfs, functions and variables
        self.post_process_workspace(ws_final)

        mc_final = self.create_model_config(mc_orig, ws_final, actual_rename_map)
        
        self.rename_objects(ws_final, mc_final)
        
        self.import_object(ws_final, mc_final, silent=False)
        self.import_class_code(ws_final)
        
        self.create_snapshots(ws_orig, mc_orig, ws_final, mc_final, rename_map)
        
        self.generate_asimov(ws_final)
        
        self.setup_parameters(ws_final)

        outname = self.config['output_file']
        outdir  = os.path.dirname(outname)
        if outdir and (not os.path.exists(outdir)):
            os.makedirs(outdir)
        ws_final.writeToFile(outname, True)
        self.stdout.info(f"INFO: Saved output workspace as \"{outname}\".")
    
    def post_process_workspace(self, ws:ROOT.RooWorkspace):
        self.add_product_terms(ws)
    
    def add_product_terms(self, ws:ROOT.RooWorkspace):
        for target_name, extra_terms in self.actions["add_product_terms"].items():
            prod_var = self.get_workspace_arg(ws, target_name, strict=True)
            if not isinstance(prod_var, ROOT.RooProduct):
                class_name = prod_var.ClassName()
                raise RuntimeError(f"failed to add product term to the variable \"{target_name}\": "
                                   f"expect a RooProduct instance but {class_name} received")
            for extra_term in extra_terms:
                member_var = self.get_workspace_arg(ws, extra_term, strict=True)
                prod_var.addTerm(member_var)
            self.stdout.info(f"INFO: The following product terms are added to the variable {target_name}: "
                             f"{', '.join(extra_terms)}")
    
    def setup_parameters(self, ws:ROOT.RooWorkspace):
        model = ExtendedModel(ws, data_name=None, verbosity="WARNING")
        model.stdout.verbosity = "INFO"
        if self.config["fix_parameters"] is not None:
            model.fix_parameters(self.config["fix_parameters"])
        if self.config["profile_parameters"] is not None:
            model.profile_parameters(self.config["profile_parameters"])
    
    def import_class_code(self, ws:ROOT.RooWorkspace):
        all_function_class = [i.ClassName().split("::")[-1] for i in ws.allFunctions()]
        all_pdf_class = [i.ClassName().split("::")[-1] for i in ws.allPdfs()]
        all_class = all_function_class + all_pdf_class
        for extension, cls in self.custom_classes.items():
            # the workspace does not use the extended class, no need to import
            if extension not in all_class:
                continue
            macro_dir = get_macro_dir(extension)
            ws.addClassDeclImportDir(macro_dir)
            ws.addClassImplImportDir(macro_dir)
            ws.importClassCode(cls)
            self.stdout.info(f"INFO: Imported class code for \"{cls.GetName()}\".")
        ws.importClassCode()

    def generate_asimov(self, ws:ROOT.RooWorkspace):
        n_asimov = len(self.actions['asimov'])
        if n_asimov == 0:
            return None
        data_name = self.config['data_name']
        asimov_handler = AsimovHandler(ws, data_name=data_name,
                                       minimizer_config=self.minimizer_config)
        for attributes in self.actions['asimov']:
            asimov_handler.generate_single_asimov(attributes)
        
    def copy_snapshot_variables(self, old_ws:ROOT.RooWorkspace, old_mc:ROOT.RooStats.ModelConfig,
                                new_ws:ROOT.RooWorkspace, new_mc:ROOT.RooStats.ModelConfig,
                                snapshot_name:str, variable_type:Union[WSVariables, str],
                                rename_map:Optional[Dict]=None):
        snapshot = old_ws.loadSnapshot(snapshot_name)
        if not snapshot:
            self.stdout.warning(f"WARNING: Snapshot {snapshot_name} not found in the original workspace")
        # get variables from orginal workspace
        variables = self.get_variables(old_mc, variable_type)
        if rename_map is None:
            rename_map = {}
        self.stdout.info(f"INFO: Copying snapshot \"{snapshot_name}\" from the original workspace "
                         "to the new workspace")
        renamed_variables_old = ROOT.RooArgSet()
        renamed_variables_new = ROOT.RooArgSet()
        for variable in variables:
            name = variable.GetName()
            if name in rename_map:
                new_name = rename_map[name]
                new_variable = new_ws.var(name)
                if not new_variable:
                    self.stdout.warning(f"WARNING: The snapshot variable \"{name}\" not found in the new workspace. Skipped.")
                # avoid modifying the original value
                _new_variable = new_variable.Clone()
                _new_variable.setVal(variable.getVal())
                _new_variable.setRange(variable.getMin(), variable.getMax())
                _new_variable.setConstant(variable.isConstant())
                _new_variable.setError(variable.getError())
                renamed_variables_old.add(variable)
                renamed_variables_new.add(_new_variable)
        variables.remove(renamed_variables_old)
        variables.add(renamed_variables_new)
        new_mc.saveSnapshot(snapshot_name, variables)
        
    def get_variables(self, mc:ROOT.RooStats.ModelConfig, variable_type:Union[WSVariables, str]):
        _variable_type = WSVariables.parse(variable_type)
        if _variable_type == WSVariables.NUISANCE_PARAMETERS:
            variables = mc.GetNuisanceParameters()
        elif _variable_type == WSVariables.GLOBAL_OBSERVABLES:
            variables = mc.GetGlobalObservables()
        elif _variable_type == WSVariables.POIS:
            variables = mc.GetParametersOfInterest()
        elif _variable_type == WSVariables.CORE:
            variables = ROOT.RooArgSet()
            variables.add(mc.GetNuisanceParameters())
            variables.add(mc.GetGlobalObservables())
            variables.add(mc.GetParametersOfInterest())
        else:
            raise RuntimeError(f"unsupported variable type: {variable_type}")
        return variables

    def create_snapshots(self, old_ws:ROOT.RooWorkspace, old_mc:ROOT.RooStats.ModelConfig,
                         new_ws:ROOT.RooWorkspace, new_mc:ROOT.RooStats.ModelConfig,
                         rename_map:Optional[Dict]=None):
        # nuisance parameter snapshots
        nuis_snapshot_names = self.config['snapshot_nuis']
        for nuis_snapshot_name in nuis_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, nuis_snapshot_name,
                                         WSVariables.NUISANCE_PARAMETERS, rename_map)
        # global observable snapshots                  
        globs_snapshot_names = self.config['snapshot_globs']
        for globs_snapshot_name in globs_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, globs_snapshot_name,
                                         WSVariables.GLOBAL_OBSERVABLES, rename_map)
        # poi snapshots 
        pois_snapshot_names = self.config['snapshot_pois']
        for pois_snapshot_name in pois_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, pois_snapshot_name,
                                         WSVariables.POIS, rename_map)
        # nuisance parameter + global observable + poi snapshots 
        vars_snapshot_names = self.config['snapshot_all']
        for vars_snapshot_name in vars_snapshot_names:
            self.copy_snapshot_variables(old_ws, old_mc, new_ws, new_mc, vars_snapshot_name,
                                         WSVariables.CORE, rename_map)
        
    def create_model_config(self, old_mc:ROOT.RooStats.ModelConfig, new_ws:ROOT.RooWorkspace,
                            rename_map:Optional[Dict]=None):
        if rename_map is None:
            rename_map = {}
            
        strict = self.config['strict']
        
        # start preparing model config
        mc_name = old_mc.GetName()
        mc = ROOT.RooStats.ModelConfig(mc_name, new_ws)

        # set pdf
        pdf_name = old_mc.GetPdf().GetName()
        pdf = new_ws.pdf(pdf_name)        
        mc.SetPdf(pdf)
        
        # set POIs
        self.stdout.debug("List of POIs in the new parameterization:")
        pois = ROOT.RooArgSet()
        poi_names = self.config['poi_names']
        # use old poi names if not specified
        if poi_names is None:
            poi_names = [i.GetName() for i in old_mc.GetParametersOfInterest()]
            poi_names = [rename_map.get(poi_name, poi_name) for poi_name in poi_names]
        for poi_name in poi_names:
            poi = self._get_relevant_variable(poi_name, new_ws, pdf)
            if not poi:
                if strict:
                    raise RuntimeError(f"POI {poi_name} does not exist")
                else:
                    self.stdout.warning(f"WARNING: POI {poi_name} does not exist. Skipping.")
                    continue
            pois.add(poi)
            self.stdout.info(f"INFO: Added POI \"{poi_name}\".")
        mc.SetParametersOfInterest(pois)
        
        # nuisance parameters and global observables from original workspace
        old_nuis = old_mc.GetNuisanceParameters()
        if old_nuis:
            nuis_names = [nuis.GetName() for nuis in old_nuis]
            nuis_names = [rename_map.get(nuis, nuis) for nuis in nuis_names]
        else:
            nuis_names = []
        old_globs = old_mc.GetGlobalObservables()
        if old_globs:
            glob_names = [glob.GetName() for glob in old_globs]
            glob_names = [rename_map.get(glob, glob) for glob in glob_names]
        else:
            glob_names = []
            
        # additional nuisance_parameters and global observables
        additional_constraints = self.actions['constraint']
        for item in additional_constraints:
            nuis_names += item['nuis']
            glob_names += item['glob']
        
        # set nuisance parameters
        nuisance_parameters = ROOT.RooArgSet()
        for nuis_name in nuis_names:
            nuis = self._get_relevant_variable(nuis_name, new_ws, pdf)
            if not nuis:
                self.stdout.warning(f"WARNING: The nuisance parameter {nuis_name} no longer exists in "
                                    "the new workspace. It will be removed from the new ModelConfig.")
                continue
            if nuis.isConstant():
                self.stdout.warning(f"WARNING: The nuisace parameter {nuis_name} is initialized as a constant. "
                                    "It will be floated in the new workspace.")
                nuis.setConstant(False)
            nuisance_parameters.add(nuis)
                
        # set global observables
        global_observables = ROOT.RooArgSet()
        for glob_name in glob_names:
            glob = self._get_relevant_variable(glob_name, new_ws, pdf)
            if not glob:
                self.stdout.warning(f"WARNING: The global observable {glob_name} no longer exists in "
                                    "the new workspace. It will be removed from the new ModelConfig.")
                continue
            if not glob.isConstant():
                self.stdout.warning(f"WARNING: The global observable {glob_name} is initialized as a floating "
                                    "parameter. It will be set to constant in the new workspace.")

                new_nuis.setConstant(True)
            global_observables.add(glob)

        # set observables
        observables = ROOT.RooArgSet()
        old_obs = old_mc.GetObservables()
        if old_obs:
            for obs in old_obs:
                obs_name = obs.GetName()
                new_obs = new_ws.obj(obs_name)
                if not new_obs:
                    raise RuntimeError(f"observable {obs_name} no longer exists in the new workspace")
                observables.add(new_obs)
        mc.SetNuisanceParameters(nuisance_parameters)
        mc.SetGlobalObservables(global_observables)
        mc.SetObservables(observables)
        
        return mc
    
    @semistaticmethod
    def extract_ws_variables(self, ws:ROOT.RooWorkspace, variables:ROOT.RooArgSet, strict:bool=True):
        extracted_variables = ROOT.RooArgSet()
        for variable in variables:
            variable_name = variable.GetName()
            extracted_variable = ws.arg(variable_name)
            if not extracted_variable:
                if strict:
                    raise RuntimeError(f"missing variable {variable_name} in the workspace {ws.GetName()}")
                else:
                    self.stdout.warning(f"WARNING: No variable {variable_name} found in the workspace {ws.GetName()}")
                    continue
            extracted_variables.add(extracted_variable, True)
        return extracted_variables

    def rename_variables(self, old_mc:ROOT.RooStats.ModelConfig, new_ws:ROOT.RooWorkspace, rename_map:Dict):
        old_var_expr = ",".join(list(rename_map.keys()))
        new_var_expr = ",".join(list(rename_map.values()))
        getattr(new_ws, "import")(old_mc.GetPdf(),
                                  ROOT.RooFit.RenameVariable(old_var_expr, new_var_expr),
                                  ROOT.RooFit.RecycleConflictNodes())
        if rename_map:
            self.stdout.info("INFO: Renamed variables\n")
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table)
        
    def rename_objects(self, ws:ROOT.RooWorkspace, mc:ROOT.RooStats.ModelConfig):
        if len(self.actions['rename']['workspace']) > 0:
            self.stdout.info("INFO: Renamed workspace\n")
            rename_map = {}
            for old_name, new_name in self.actions['rename']['workspace'].items():
                rename_map[ws.GetName()] = new_name
                ws.SetName(new_name)
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table)
        if len(self.actions['rename']['model_config']) > 0:
            self.stdout.info("INFO: Renamed model config\n")
            rename_map = {}
            for old_name, new_name in self.actions['rename']['model_config'].items():
                rename_map[mc.GetName()] = new_name
                mc.SetName(new_name)
            rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
            self.stdout.info(rename_table)
        if len(self.actions['rename']['dataset']) > 0:
            rename_map = {}            
            for old_name, new_name in self.actions['rename']['dataset'].items():
                if old_name == new_name:
                    continue
                dataset = ws.data(old_name)
                if not dataset:
                    raise RuntimeError(f"dataset \"{old_name}\" not found in the original workspace")
                check_dataset = ws.data(new_name)
                if check_dataset:
                    raise RuntimeError(f"cannot rename dataset from \"{old_name}\" to \"{new_name}\": "
                                       f"the dataset \"{new_name}\" already exists in the original workspace")
                rename_map[old_name] = new_name
                dataset.SetName(new_name)
            if rename_map:
                self.stdout.info("INFO: Renamed dataset\n")
                rename_table = "\n".join(self.get_name_mapping_str_arrays(rename_map))
                self.stdout.info(rename_table)                
        
    def import_datasets(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        datasets = old_ws.allData()
        for dataset in datasets:
            getattr(new_ws, "import")(dataset)
            self.stdout.info(f"INFO: Imported dataset \"{dataset.GetName()}\".")
            
    def redefine_objects(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        flag = False
        for i, expr in enumerate(self.actions['redefine']):
            self.stdout.info(f"INFO: (Item {i}) {expr}")
            obj_name, obj_type = self._get_object_name_and_type_from_expr(expr)
            arg = old_ws.arg(obj_name)
            if not arg:
                raise RuntimeError(f"object {obj_name} does not exist in the original workspace")
            if obj_type == WSObjectType.VARIABLE:
                result = re.search(r"\[(.+)\]", expr)
                if not result:
                    raise RuntimeError(f"invalid variable expression {expr}")
                self.import_expression(new_ws, expr)
                new_var = new_ws.var(obj_name)
                tokens = result.group(1).split(",")
                # only modify the value
                if len(tokens) == 1:
                    old_range = arg.getRange()
                    # need to restore the range
                    new_var.setRange(old_range[0], old_range[1])
                # only modify the range
                elif len(tokens) == 2:
                    # need to restore the value
                    new_var.setVal(arg.getVal())
                # need to restore constant state
                new_var.setConstant(arg.isConstant())
            else:
                self.import_expression(new_ws, expr)
            flag = True
        return flag
        
    def implement_objects(self, ws:ROOT.RooWorkspace):
        flag = False
        for i, expr in enumerate(self.actions['define']):
            self.stdout.info(f"INFO: (Item {i}) {expr}")
            if "FlexibleInterpVar" in expr:
                self.implement_flexible_interp_var(ws, expr)
            elif "RooMultiVarGaussian" in expr:
                self.implement_multi_var_gaussian(ws, expr)
            else:
                self.import_expression(ws, expr)
            flag = True
        return flag
                
    def implement_external_pdfs(self, ws:ROOT.RooWorkspace):
        flag = False
        for i, item in enumerate(self.actions['constraint']):
            pdf_name = item['pdf']
            file = item['file']
            if file is not None:
                self.load_external_pdf(file, pdf_name, ws)
                self.stdout.info(f"INFO: Loaded external pdf {pdf_name} from {file}")
                flag = True
        return flag
                
    def load_external_pdf(self, ext_rfile:str, pdf_name:str, ws:ROOT.RooWorkspace):
        model = ExtendedModel(ext_rfile, data_name=None, verbosity="WARNING")
        pdf = model.workspace.pdf(pdf_name)
        if not pdf:
            raise RuntimeError(f"pdf {pdf_names} not found in the workspace loaded from {ext_rfile}")
        self.import_object(ws, pdf)
    
    def get_actual_rename_map(self, rename_map:Dict, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        actual_rename_map = {}
        for old_name, new_name in rename_map.items():
            # if the object with the new name isalready defined, it's not a renaming
            if (old_ws.arg(new_name)) or (new_ws.arg(new_name)):
                continue
            actual_rename_map[old_name] = new_name
        return actual_rename_map
    
    def get_rename_map(self, old_ws:ROOT.RooWorkspace, new_ws:ROOT.RooWorkspace):
        rename_map = {}
        #regex = re.compile(r"\(([\w=,]+)\)")
        regex = re.compile(r"\((.+)\)")
        strict = self.config['strict']
        # rename definitions from the "Map" node
        for expr in self.actions['map']:
            match = regex.search(expr)
            if not match:
                raise RuntimeError(f"invalid expression for a map: {expr}")
            rename_str = [i for i in match.group(1).split(",") if i]
            if len(rename_str) < 2:
                raise RuntimeError(f"no members found for a map: {expr}")
            rename_str = rename_str[1:]
            for item in rename_str:
                tokens = item.split("=")
                if len(tokens) != 2:
                    raise RuntimeError(f"invalid rename syntax: {item}")
                old_name = tokens[0]
                new_name = tokens[1]
                if not old_ws.arg(old_name):
                    if strict:
                        raise RuntimeError(f"object {old_name} (-> {new_name}) does not exist in the original workspace")
                    else:
                        self.stdout.warning(f"object {old_name} does not exist in the original workspace, skipping...")
                        continue
                if not new_ws.arg(new_name):
                    raise RuntimeError(f"object {new_name} (<- {old_name}) does not exist in the temporary workspace")
                if old_name in rename_map:
                    raise RuntimeError(f"object {old_name} is renamed more than once")
                rename_map[old_name] = new_name
        # rename definitions from the "Rename" node
        for old_name, new_name in self.actions['rename']['variable'].items():
            if not old_ws.arg(old_name):
                if strict:
                    raise RuntimeError(f"object {old_name} (-> {new_name}) does not exist int the original workspace")
                else:
                    self.stdout.warning(f"object {old_name} does not exist in the original workspace, skipping...")
                    continue
            if old_name in rename_map:
                raise RuntimeError(f"object {old_name} is renamed more than once")
            rename_map[old_name] = new_name
        return rename_map
    
    def remake_simultaneous_pdf(self, old_mc:ROOT.RooStats.ModelConfig, new_ws:ROOT.RooWorkspace):
        pdf_name = old_mc.GetPdf().GetName()
        pdf = new_ws.pdf(pdf_name)
        if not pdf:
            raise RuntimeError(f"pdf {pdf_name} does not exist in workspace {new_ws.GetName()}")
        category = pdf.indexCat()
        n_cat = len(category)
        
        observables = self.extract_ws_variables(new_ws, old_mc.GetObservables(), True)
        nuisance_parameters = self.extract_ws_variables(new_ws, old_mc.GetNuisanceParameters(), False)

        pdf_map = {}
        
        for i in range(n_cat):
            category.setBin(i)
            category_name = category.getLabel()
            self.stdout.info(f"INFO: Creating new pdf for the category {category_name}")
            pdf_i = pdf.getPdf(category_name)
            
            base_components = ROOT.RooArgSet()
            obs_terms = ROOT.RooArgList()
            dis_constraints = ROOT.RooArgList()
            ROOT.RooStats.FactorizePdf(observables, pdf_i, obs_terms, dis_constraints)
            base_components.add(obs_terms)
            
            # remove constraint pdfs that are no longer needed
            if dis_constraints.getSize() > 0:
                constraints = pdf_i.getAllConstraints(observables, nuisance_parameters, True)
                base_components.add(constraints)
            
            # adding additional constraint pdf
            for i, item in enumerate(self.actions['constraint']):
                pdf_name = item['pdf']
                nuis_names = item['nuis']
                glob_names = item['glob']
                new_pdf = new_ws.pdf(pdf_name)
                if not new_pdf:
                    raise RuntimeError(f"pdf {pdf_name} does not exist in the new workspace")
                # check whether the current category depends on the constraint pdf
                for nuis_name in nuis_names:
                    nuis_var = self._get_relevant_variable(nuis_name, new_ws, pdf_i)
                    if nuis_var is not None:
                        base_components.add(new_pdf)
                        break
            new_pdf_name = f"{pdf_i.GetName()}__addConstr"
            pdf_map[category_name] = ROOT.RooProdPdf(new_pdf_name, new_pdf_name, base_components)
        c_pdf_map = ExtendedModel.get_pdf_map(pdf_map)
        pdf_name = old_mc.GetPdf().GetName()
        sim_pdf = ROOT.RooSimultaneous(pdf_name, f"{pdf_name}__addConstr", c_pdf_map, category)
        return sim_pdf
    
    @staticmethod
    def _get_relevant_variable(var_name:str, ws:ROOT.RooWorkspace, pdf:ROOT.RooAbsPdf, warn:bool=False):
        var = ws.var(var_name)
        if not var:
            if warn:
                self.stdout.warning(f"WARNING: Variable {var_name} does not exist in the new workspace")
            return None
        if not pdf.dependsOn(var):
            if warn:
                self.stdout.warning(f"WARNING: Variable {var_name} exists in the new workspace but is "
                                    f"not part of the provided pdf {pdf.GetName()}")
            return None
        return var
        
    def implement_flexible_interp_var(self, ws:ROOT.RooWorkspace, expr:str):
        # parse attributes
        expr = re.sub('\s+', '', expr)
        program = re.compile(r"FlexibleInterpVar::(?P<name>[\w]+)\((?P<NPName>[\w,]+),"
                             r"(?P<nominal>[\w,]+),(?P<errHi>[\w,]+),(?P<errLo>[\w,]+),"
                             r"(?P<interpolation>[\w,]+)\)")
        result = program.search(expr)
        if not result:
            raise RuntimeError(f"invalid format for FlexibleInterpVar definition: {expr}")
        groups = result.groupdict()
        response_name = groups['name']
        nuis_name     = groups['NPName']
        nominal       = float(groups['nominal'])
        error_hi      = float(groups['errHi'])
        error_lo      = float(groups['errLo'])
        interpolation = int(groups['interpolation'])
        
        sigma_var_low = np.array([nominal + error_lo])
        sigma_var_high = np.array([nominal + error_hi])
        code = np.array([interpolation])
        
        nuis_arglist = ROOT.RooArgList()
        nuis = self.get_workspace_arg(ws, nuis_name)
        nuis_arglist.add(nuis)
        
        function = ROOT.RooStats.HistFactory.FlexibleInterpVar(response_name, response_name, nuis_arglist,
                                                               nominal, sigma_var_low, sigma_var_high, code)
        self.import_object(ws, function)
        self.stdout.info(f"INFO: Implemented FlexibleInterpVar \"{response_name}\"")
        self.stdout.info(str(py_V))

    
    def implement_multi_var_gaussian(self, ws:ROOT.RooWorkspace, expr:str):
        # parse attributes
        expr = re.sub('\s+', '', expr)
        program = re.compile(r"RooMultiVarGaussian::(?P<name>[\w]+)\({(?P<obsList>[\w,]+)}:"
                             r"{(?P<meanList>[\w,]+)}:{(?P<uncertList>[\w,]+)}:"
                             r"{(?P<correlationList>[\w,]+)}\)")
        result = program.search(expr)
        if not result:
            raise RuntimeError(f"invalid format for RooMultiVarGaussian definition: {expr}")
        groups = result.groupdict()
        function_name    = groups['name']
        obs_list         = groups['obsList'].split(",")
        mean_list        = groups['meanList'].split(",")
        uncert_list      = groups['uncertList'].split(",")
        correlation_list = groups['correlationList'].split(",")
        
        n_poi = len(obs_list)
        if not all(len(l) == n_poi for l in [obs_list, mean_list, uncert_list]):
            raise RuntimeError(f"number of items in each argument group of a RooMultiVarGaussian "
                               f"definition must be equal: {expr}")
        if len(correlation_list) != (n_poi * (n_poi - 1) // 2):
            raise RuntimeError("number of correlation matrix elements must be N * (N-1) / 2, where "
                               "N is the dimension of the matrix")
        obs_arglist = ROOT.RooArgList()
        mean_arglist = ROOT.RooArgList()
        for i in range(n_poi):
            obs_name = obs_list[i]
            mean_name = mean_list[i]
            obs = self.get_workspace_arg(ws, obs_name)
            obs_arglist.add(obs)
            mean = self.get_workspace_arg(ws, mean_name)
            mean_arglist.add(mean)
        V = ROOT.TMatrixDSym(n_poi)
        py_V = np.zeros(n_poi * n_poi).reshape(n_poi, n_poi)
        index = 0
        for i in range(n_poi):
            for j in range(i, n_poi):
                if (i == j):
                    v = float(uncert_list[i])
                    V[i, i] = v * v
                    py_V[i, i] = v * v
                elif (i < j):
                    v = float(correlation_list[index]) * float(uncert_list[i]) * float(uncert_list[j])
                    V[i, j] = v
                    V[j, i] = v
                    py_V[i, j] = v
                    py_V[j, i] = v
                    index += 1
        function = RooMultiVarGaussian(function_name, function_name, obs_arglist, mean_arglist, V)
        self.import_object(ws, function)
        self.stdout.info(f"INFO: Implemented RooMultiVarGaussian \"{function_name}\" with correlation matrix")
        self.stdout.info(str(py_V))