import os
import re
import json
import time
from typing import Optional, Union, List, Dict

import numpy as np

import ROOT
from ROOT.RooPrintable import (kName, kClassName, kValue, kArgs, kExtras, kAddress,
                               kTitle, kCollectionHeader, kSingleLine)

import quickstats
from quickstats import semistaticmethod, Timer
from quickstats.components import AbstractObject, ExtendedModel
from quickstats.utils.io import Verbosity, get_colored_text, format_comparison_text
from quickstats.utils.root_utils import load_macro, get_macro_dir
from quickstats.maths.numerics import is_float, pretty_value
from quickstats.components.basics import WSVariables
from quickstats.utils.general_enum import GeneralEnum
from quickstats.interface.root.roofit_extension import get_str_data

kUnique        = 0b00001
kRedefined     = 0b00010
kReconstituted = 0b00100
kRenamed       = 0b01000
kIdentical     = 0b10000

class WSItemType(GeneralEnum):
    
    PDF      = (0, kClassName|kName|kArgs , kSingleLine)
    FUNCTION = (1, kClassName|kName|kArgs , kSingleLine)
    VARIABLE = (2, kName|kValue|kExtras   , kSingleLine)
    OTHER    = (3, 0                      , kSingleLine)
    
    def __init__(self, enum_id:int, default_content:int, default_style:int):
        self.enum_id         = enum_id
        self.default_content = default_content
        self.default_style   = default_style
    
class WSItem(GeneralEnum):
    
    WORKSPACE                        = (0,  WSItemType.OTHER, 'Workspace', None, False, False, 0b11001)
    CATEGORY                         = (1,  WSItemType.OTHER, 'Categories', None, True, False, 0b10011)
    SNAPSHOT                         = (2,  WSItemType.OTHER, 'Snapshots', None, False, False, 0b10011)
    DATASET                          = (3,  WSItemType.OTHER, 'Datasets', None, False, False, 0b11011)
    PDF                              = (4,  WSItemType.PDF, 'Pdfs', None, True, True, 0b01011)
    FUNCTION                         = (5,  WSItemType.FUNCTION, 'Functions', None, True, True, 0b01011)
    POI                              = (6,  WSItemType.VARIABLE, 'POIs', WSVariables.POIS, True, False, 0b01011)
    NUISANCE_PARAMETER               = (7,  WSItemType.VARIABLE, 'Nuisance Parameters',
                                        WSVariables.NUISANCE_PARAMETERS, True, False, 0b01011)
    GLOBAL_OBSERVABLE                = (8,  WSItemType.VARIABLE, 'Global Observables',
                                        WSVariables.GLOBAL_OBSERVABLES, True, False, 0b01011)    
    CONSTRAINED_NUISANCE_PARAMETER   = (9,  WSItemType.VARIABLE, 'Constrained Nuisance Parameters',
                                        WSVariables.CONSTRAINED_NUISANCE_PARAMETERS, True, False, 0b01011)
    UNCONSTRAINED_NUISANCE_PARAMETER = (10, WSItemType.VARIABLE, 'Unconstrained Nuisance Parameters',
                                        WSVariables.UNCONSTRAINED_NUISANCE_PARAMETERS, True, False, 0b01011)
    AUXILIARY                        = (11, WSItemType.VARIABLE, 'Auxiliary Variables',
                                        WSVariables.AUXILIARY, True, False, 0b01011)
    NON_CONSTRAINT_VARIABLE          = (12, WSItemType.VARIABLE, 'Non-constraint Variables',
                                        WSVariables.NON_CONSTRAINT_VARIABLES, True, False, 0b01011)
    
    def __init__(self, enum_id:int, item_type:WSItemType, title:str, var_repr:Optional[WSVariables],
                 support_definition:bool, is_composite:bool, default_visibility:int):
        self.enum_id   = enum_id
        self.item_type = item_type
        self.title     = title
        self.var_repr  = var_repr
        self.support_definition = support_definition
        self.is_composite = is_composite
        self.default_visibility = default_visibility
            
class ComparisonData:

    def __init__(self, title:str="", support_definition:bool=True, is_composite:bool=False):
        self.title = title
        self.support_definition = support_definition
        self.is_composite = is_composite
        self.reset()
        
    @classmethod
    def from_WSItem(cls, item:WSItem):
        title = item.title
        support_definition = item.support_definition
        is_composite = item.is_composite
        instance = cls(title=title, support_definition=support_definition, is_composite=is_composite)
        return instance
    
    @classmethod
    def from_dataframe(cls, item:WSItem, df:"pandas.DataFrame"):
        instance = cls.from_WSItem(item)
        instance.df_merge = df
        instance._restore_raw_df()
        return instance
    
    def reset(self):
        import pandas as pd
        self.df_1 = pd.DataFrame({"name":[], "class":[], "definition":[]})
        self.df_2 = pd.DataFrame({"name":[], "class":[], "definition":[]})
        self.df_merge = None
        self.df_factorized = None
        self.possible_mappings = None

    def set_title(self, title:str):
        self.title = title
        
    def add_single(self, name_1:Optional[str]=None, name_2:Optional[str]=None,
                   definition_1:str="", definition_2:str="",
                   class_1:str="", class_2:str=""):
        import pandas as pd
        if name_1 is not None:
            df_1 = pd.DataFrame.from_records([{"name": name_1, "class": "", "definition": definition_1}])
            self.df_1 = pd.concat([self.df_1, df_1], ignore_index=True)
        if name_2 is not None:
            df_2 = pd.DataFrame.from_records([{"name": name_2, "class": "", "definition": definition_2}])
            self.df_2 = pd.concat([self.df_2, df_2], ignore_index=True)
        
    def add(self, df_1:Optional["pandas.DataFrame"]=None, df_2:Optional["pandas.DataFrame"]=None):
        import pandas as pd
        if df_1 is not None:
            self.df_1 = pd.concat([self.df_1, df_1], ignore_index=True)
        if df_2 is not None:
            self.df_2 = pd.concat([self.df_2, df_2], ignore_index=True)
            
    def factorize_definition(self):
        regex = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)")
        df = self.get_df("redefined")
        args_left = df['definition_left'].str.findall(regex)
        args_right = df['definition_right'].str.findall(regex)
        df.loc[:, ['args_left']] = args_left
        df.loc[:, ['args_right']] = args_right
        df = df[['name', 'definition_left', 'definition_right', 'args_left', 'args_right']]
        df['nargs_left'] = df['args_left'].apply(len)
        df['nargs_right'] = df['args_right'].apply(len)
        df['same_nargs'] = df['nargs_left'] == df['nargs_right']
        self.df_factorized = df
    
    def evaluate_possible_mappings(self):
        if self.df_factorized is None:
            self.factorize_definition()
        target_df = self.df_factorized[self.df_factorized["same_nargs"]]
        a = target_df['args_left'].values
        b = target_df['args_right'].values
        names = target_df['name'].values
        results = {}
        statistics = {}
        size = len(a)
        for i in range(size):
            a_i = a[i]
            b_i = b[i]
            name_i = names[i]
            size_i = len(a_i)
            result_i = {}
            count_i = {}
            for j in range(size_i):
                a_ij = a[i][j]
                b_ij = b[i][j]
                if a_ij != b_ij:
                    if a_ij not in count_i:
                        count_i[a_ij] = 0
                    result_i[a_ij] = b_ij
                    count_i[a_ij] += 1
            for a_ij, count in count_i.items():
                if count != 1:
                    result_i.pop(a_ij)
                else:
                    if a_ij not in statistics:
                        statistics[a_ij] = {"candidates":[], "counts": {"total": 0}}
                    b_ij = result_i[a_ij]
                    if b_ij not in statistics[a_ij]["candidates"]:
                        statistics[a_ij]["candidates"].append(b_ij)
                        statistics[a_ij]["counts"][b_ij] = 0
                    statistics[a_ij]["counts"][b_ij] += 1
                    statistics[a_ij]["counts"]["total"] += 1
            results[name_i] = result_i
        self.possible_mappings = results
        self.mapping_statistics = statistics
    
    @staticmethod
    def _get_combined_mapping_statistics(all_mappings:List[Dict]):
        combined_mapping = {}
        for mapping in all_mappings:
            for key, value in mapping.items():
                if key not in combined_mapping:
                    combined_mapping[key] = {"candidates":[], "counts":{"total":0}}
                for candidate in value["candidates"]:
                    if candidate not in combined_mapping[key]["candidates"]:
                        combined_mapping[key]["candidates"].append(candidate)
                for candidate, count in value["counts"].items():
                    if candidate not in combined_mapping[key]["counts"]:
                        combined_mapping[key]["counts"][candidate] = 0
                    combined_mapping[key]["counts"][candidate] += count
        return combined_mapping
    
    def process_mappings(self, mappings:Dict):
        if self.df_merge is None:
            self.process()
        df = self.df_merge
        df.set_index("name", inplace=True)
        for name_1, name_2 in mappings.items():
            if name_1 in df.index:
                series_1 = df.loc[name_1]
                if series_1['_merge'] != "left_only":
                    continue
                # object type did not change
                if name_2 in df.index:
                    series_2 = df.loc[name_2]
                    definition_1 = series_1['definition_left']
                    # remove original name by the new name in the definition
                    definition_1 = re.sub(r"\b%s\b" % name_1, name_2, definition_1)
                    definition_2 = series_2['definition_right']
                    df.loc[name_1, ["name_alt"]] = name_2
                    df.loc[name_2, ["name_alt"]] = name_1
                    # different name, same definition
                    if definition_1 == definition_2:
                        df.loc[name_1, ["category"]] = "renamed"
                        df.loc[name_2, ["category"]] = "renamed"
                    # different name, different definition
                    else:
                        df.loc[name_1, ["category"]] = "remapped"
                        df.loc[name_2, ["category"]] = "remapped"
                    continue
                else:
                    # object mapped to object of another type
                    df.loc[name_1, ["name_alt"]] = name_2
                    df.loc[name_1, ["category"]] = "remapped"
                    
            if name_2 in df.index:
                series_2 = df.loc[name_2]
                if series_2['_merge'] != "right_only":
                    continue
                # object mapped to object of another type
                df.loc[name_2, ["name_alt"]] = name_1
                df.loc[name_2, ["category"]] = "remapped"
        df.reset_index(inplace=True)
        
    def process(self):
        df_merge = self.df_1.merge(self.df_2, on="name", how='outer', indicator=True, sort=True,
                                   suffixes=('_left', '_right'), validate="one_to_one")
        df_merge['same_definition'] = df_merge['definition_left'] == df_merge['definition_right']
        columns = ["name", "definition_left", "definition_right", "class_left", "class_right"]
        import pandas as pd
        df_merge[columns] = df_merge[columns].astype(str)
        regex = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)")
        expression_left  = df_merge['definition_left'].str.replace(regex, "")
        expression_right = df_merge['definition_right'].str.replace(regex, "")
        df_merge['same_expression'] = expression_left == expression_right
        df_merge['category'] = df_merge['_merge']
        new_categories = ["identical", "redefined", "reconstituted", "renamed", "remapped"]
        df_merge['category'] = df_merge['category'].cat.add_categories(new_categories)
        mask_identical = (df_merge['_merge'] == "both") & (df_merge['same_definition'])
        mask_redefined = (df_merge['_merge'] == "both") & (~df_merge['same_definition'])
        df_merge.loc[mask_identical, ['category']] = 'identical'
        df_merge.loc[mask_redefined, ['category']] = 'redefined'
        df_merge['name_alt'] = None
        self.df_merge = df_merge
        
        if self.is_composite:
            self.factorize_definition()
            self.evaluate_possible_mappings()
        
    def get_df(self, category:str="any"):
        """
            Return a copy of the core dataframe.
            Arguments:
                category: str
                    Filter the dataframe by criteria. Allowed choices:
                    identical     = same name, same definition
                    redefined     = same name, different definition
                    reexpressed   = same name, different expression
                    reconstituted = same name, same expression, different constituents
                    left_only     = different name, found in left only
                    right_only    = different name, found in right only
                    unique_left   = different name, found in left only, no common server with right
                    unique_right  = different name, found in right only, no common server with right                   
                    renamed       = different name, same definition, same servers
                    remapped      = different name, different definition, same servers
                    common        = same name
                    distinct      = different_name
                    left          = everything found in left
                    right         = everything found in left
                    any           = everything
        """
        if self.df_merge is None:
            self.process()
        if category == "any":
            df = self.df_merge
        elif category in ["common", "identical", "redefined", "reexpressed", "reconstituted"]:
            df = self.df_merge[self.df_merge['_merge'] == "both"]
            if category == "identical":
                df = df[df['category'] == "identical"]
            elif category in ["redefined", "reexpressed", "reconstituted"]:
                df = df[df['category'] == "redefined"]
                if category == "reexpressed":
                    df = df[~df['same_expression']]
                if category == "reconstituted":
                    df = df[df['same_expression']]
        elif category in ["distinct", "renamed", "remapped"]:
            df = self.df_merge[self.df_merge['_merge'] != "both"]
            if category == "renamed":
                df = df[df['category'] == "renamed"]
            elif category == "remapped":
                df = df[df['category'] == "remapped"]
        elif category == "left_only":
            df = self.df_merge[self.df_merge['_merge'] == "left_only"]
        elif category == "right_only":
            df = self.df_merge[self.df_merge['_merge'] == "right_only"]
        elif category == "unique_left":
            df = self.df_merge[self.df_merge['category'] == "left_only"]
        elif category == "unique_right":
            df = self.df_merge[self.df_merge['category'] == "right_only"]
        elif category == "left":
            df = self.df_merge[self.df_merge['_merge'] != "right_only"]
        elif category == "right":
            df = self.df_merge[self.df_merge['_merge'] != "left_only"]
        else:
            raise ValueError('invalid category (choose from "identical", "redefined", "reconstituted", '
                             '"reexpressed", "left_only", "right_only", "unique_left", "unique_right", '
                             '"renamed", "remapped", "common", "distinct", "any")')
        # make a copy and reset index
        df = df.reset_index(drop=True)
        return df
    
    def _restore_raw_df(self):
        if self.df_merge is None:
            raise RuntimeError("no merged dataframe to restore")
        df = self.df_merge
        df_1 = df[df['_merge'] != "right_only"][['name','class_left', 'definition_left']]
        df_1 = df_1.rename(columns={"class_left":"class", "definition_left":"defintion"})
        df_2 = df[df['_merge'] != "left_only"][['name','class_right', 'definition_right']]
        df_2 = df_1.rename(columns={"class_right":"class", "definition_right":"defintion"})
        self.df_1 = df_1
        self.df_2 = df_2
        if self.is_composite:
            self.factorize_definition()
            self.evaluate_possible_mappings()
            
    def _get_content_summary_str(self, contents:List[str], title:str, title_color:str,
                                 content_color:str, indent:str="   ", show_content:bool=True):
        summary_str = ""
        size = len(contents)
        if size > 0:
            s = f"{indent}[{title} ({size})]\n"
            summary_str += get_colored_text(s, title_color)
            if not show_content:
                return summary_str
            for content in contents:
                s = f"{indent*2}{content}\n"
                summary_str += get_colored_text(s, content_color)
        return summary_str
    
    def _get_mapped_content_summary_str(self, contents_1:List[str], contents_2:List[str],
                                        title:str, title_color:str,
                                        equal_color:Optional[str]=None,
                                        delete_color:str="red",
                                        insert_color:str="green",
                                        indent:str="   ",
                                        show_content:bool=True):
        summary_str = ""
        size_1 = len(contents_1)
        size_2 = len(contents_2)
        if size_1 != size_2:
            raise ValueError("content_1 and content_2 must have the same size")
        if size_1 > 0:
            s = f"{indent}[{title} ({size_1})]\n"
            summary_str += get_colored_text(s, title_color)
            if not show_content:
                return summary_str
            for (content_1, content_2) in zip(contents_1, contents_2):
                s_left, s_right = format_comparison_text(content_1, content_2,
                                                         equal_color, delete_color, insert_color)
                summary_str += f"{indent*2}{s_left} -> {s_right}\n"
        return summary_str
    
    def _get_redef_mapping_contents(self, df:"pandas.DataFrame"):
        contents = df[['definition_left', 'definition_right']].to_dict('list')
        contents_1 = contents["definition_left"]
        contents_2 = contents["definition_right"]
        return contents_1, contents_2
    
    def _get_ext_mapping_contents(self, df:"pandas.DataFrame", ext_ref:Optional[Dict]=None):
        if ext_ref is None:
            ext_ref = {}
        df_1 = df[df["_merge"] == "left_only"]
        df_2 = df[df["_merge"] == "right_only"].set_index("name")
        alt_names = df_1["name_alt"].values
        contents_1 = list(df_1["definition_left"].values)
        contents_2 = []
        for alt_name in alt_names:
            if alt_name in df_2.index:
                definition = df_2.loc[alt_name]["definition_right"]
                contents_2.append(definition)
            else:
                if alt_name in ext_ref:
                    contents_2.append(ext_ref[alt_name])
                else:
                    contents_2.append(f"{alt_name} [definition not inferred]")
        return contents_1, contents_2
    
    def get_summary_str(self, visibility:int=0b00011, indent:str="   ",
                        ext_ref:Optional[Dict]=None):
        """
            Arguments:
                visibility: integer
                    boolean mask for showing definitions of certain objects
                    0b00001 = show definitions for unique objects
                    0b00010 = show definitions for redefined objects
                    0b00100 = show definitions for reconstituted objects
                    0b01000 = show definitions for renamed/remapped objects
                    0b10000 = show definitions for identical objects
        """
        if ext_ref is None:
            ext_ref = {}
        s = f"{self.title}:\n"
        summary_str = get_colored_text(s, "bright magenta")
        if self.support_definition:
            df = self.get_df("identical")
            content_kwargs = {
                "contents": df['definition_left'].values,
                "title": "Common Object (Identical Definition)",
                "title_color": "bright yellow",
                "content_color": "green",
                "indent": indent,
                "show_content": visibility & kIdentical
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
            if self.is_composite:
                df = self.get_df("reconstituted")
                contents_1, contents_2 = self._get_redef_mapping_contents(df)
                content_kwargs = {
                    "contents_1": contents_1,
                    "contents_2": contents_2,
                    "title": "Common Object (Same Expression, Modified Members)",
                    "title_color": "bright yellow",
                    "indent": indent,
                    "show_content": visibility & kReconstituted
                }
                summary_str += self._get_mapped_content_summary_str(**content_kwargs)
                df = self.get_df("reexpressed")
                contents_1, contents_2 = self._get_redef_mapping_contents(df)
                content_kwargs = {
                    "contents_1": contents_1,
                    "contents_2": contents_2,
                    "title": "Common Object (Modified Expression)",
                    "title_color": "bright yellow",
                    "indent": indent,
                    "show_content": visibility & kRedefined
                }
                summary_str += self._get_mapped_content_summary_str(**content_kwargs)
            else:
                df = self.get_df("redefined")
                contents_1, contents_2 = self._get_redef_mapping_contents(df)
                content_kwargs = {
                    "contents_1": contents_1,
                    "contents_2": contents_2,
                    "title": "Common Object (Modified Definition)",
                    "title_color": "bright yellow",
                    "indent": indent,
                    "show_content": visibility & kRedefined
                }
                summary_str += self._get_mapped_content_summary_str(**content_kwargs)
            
            df = self.get_df("renamed")
            contents_1, contents_2 = self._get_ext_mapping_contents(df, ext_ref)
            content_kwargs = {
                "contents_1": contents_1,
                "contents_2": contents_2,
                "title": "Renamed Object (Modified Name, Same Definition)",
                "title_color": "bright yellow",
                "indent": indent,
                "show_content": visibility & kRenamed
            }
            summary_str += self._get_mapped_content_summary_str(**content_kwargs)
            
            df = self.get_df("remapped")
            contents_1, contents_2 = self._get_ext_mapping_contents(df, ext_ref)
            content_kwargs = {
                "contents_1": contents_1,
                "contents_2": contents_2,
                "title": "Remapped Object (Modified Name, Modified Definition)",
                "title_color": "bright yellow",
                "indent": indent,
                "show_content": visibility & kRenamed
            }
            summary_str += self._get_mapped_content_summary_str(**content_kwargs)            
            
            df = self.get_df("unique_left")
            content_kwargs = {
                "contents": df["definition_left"].values,
                "title": "Unique Object (Left)",
                "title_color": "bright yellow",
                "content_color": "red",
                "indent": indent
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
            
            df = self.get_df("unique_right")
            content_kwargs = {
                "contents": df["definition_right"].values,
                "title": "Unique Object (Right)",
                "title_color": "bright yellow",
                "content_color": "red",
                "indent": indent
            }            
            summary_str += self._get_content_summary_str(**content_kwargs)
        else:
            content_kwargs = {
                "contents": self.get_df("identical")['name'].values,
                "title": "Common Object",
                "title_color": "bright yellow",
                "content_color": "green",
                "indent": indent,
                "show_content": visibility & kIdentical
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
            content_kwargs = {
                "contents": self.get_df("redefined")['name'].values,
                "title": "Common Object (Modified Definition)",
                "title_color": "bright yellow",
                "content_color": "green",
                "indent": indent,
                "show_content": visibility & kRedefined
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
            df = self.get_df("renamed")
            df = df[df["_merge"] == "left_only"]
            content_kwargs = {
                "contents_1": df["name"].values,
                "contents_2": df["name_alt"].values,
                "title": "Renamed Object (Modified Name, Same Definition)",
                "title_color": "bright yellow",
                "indent": indent,
                "show_content": visibility & kRenamed
            }
            summary_str += self._get_mapped_content_summary_str(**content_kwargs)
            content_kwargs = {
                "contents": self.get_df("unique_left")['name'].values,
                "title": "Unique Object (Left)",
                "title_color": "bright yellow",
                "content_color": "red",
                "indent": indent,
                "show_content": visibility & kUnique
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
            content_kwargs = {
                "contents": self.get_df("unique_right")['name'].values,
                "title": "Unique Object (Right)",
                "title_color": "bright yellow",
                "content_color": "red",
                "indent": indent,
                "show_content": visibility & kUnique
            }
            summary_str += self._get_content_summary_str(**content_kwargs)
        return summary_str

class WSComparer(AbstractObject):
    
    kDefaultItems = [WSItem.WORKSPACE, WSItem.CATEGORY, WSItem.DATASET, WSItem.POI,
                     WSItem.PDF, WSItem.FUNCTION, WSItem.NUISANCE_PARAMETER,
                     WSItem.GLOBAL_OBSERVABLE, WSItem.AUXILIARY]
    
    @property
    def target_items(self) -> Union[List[str], List[WSItem]]:
        return self._target_items
    
    @target_items.setter
    def target_items(self, other:Optional[Union[List[str], List[WSItem], WSItem, str]]=None) -> None:
        self._target_items = self._parse_items(other)
        
    @property
    def visibility_map(self) -> Dict[str, int]:
        return self._visibility_map
    
    @visibility_map.setter
    def visibility_map(self, source:Optional[Union[str, Dict]]=None):
        if source is None:
            self._visibility_map = {}
        elif isinstance(source, dict):
            visibility_map = {}
            for key, value in source.items():
                item = WSItem.parse(key)
                item_str = item.name.lower()
                if isinstance(value, str):
                    value = int(value, 2)
                visibility_map[item_str] = value
            self._visibility_map = visibility_map
        elif isinstance(source, str):
            expressions = source.split(",")
            visibility_map = {}
            for expression in expressions:
                tokens = expression.split("=")
                if len(tokens) != 2:
                    raise ValueError("invalid string format for setting visibility")
                item_str = tokens[0]
                value = tokens[1]
                visibility_map[item_str] = value
            self.visibility_map = visibility_map
        else:
            raise ValueError("unknown argument type for setting visibility")
                       
    def __init__(self, ws_path_1:Optional[str]=None, ws_path_2:Optional[str]=None,
                 items:Optional[Union[List[str], List[WSItem], WSItem, str]]=None,
                 visibility_map:Optional[Union[str, Dict]]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(verbosity=verbosity)
        
        if (ws_path_1 is not None) and (ws_path_2 is not None):
            self.set_targets(ws_path_1, ws_path_2)
        else:
            self.model_1 = None
            self.model_2 = None
            
        self.item_contents = {
            WSItemType.PDF      : WSItemType.PDF.default_content,
            WSItemType.FUNCTION : WSItemType.FUNCTION.default_content,
            WSItemType.VARIABLE : WSItemType.VARIABLE.default_content
        }
        self.item_styles = {
            WSItemType.PDF      : WSItemType.PDF.default_style,
            WSItemType.FUNCTION : WSItemType.FUNCTION.default_style,
            WSItemType.VARIABLE : WSItemType.VARIABLE.default_style,
        }
        
        self.target_items = items
        self.visibility_map = visibility_map
        self.data = {}

    def set_targets(self, ws_path_1:str, ws_path_2:str):
        self.stdout.info(f"INFO: Initializing targets...")
        with Timer() as t:
            self.model_1 = ExtendedModel(ws_path_1, data_name=None, verbosity="WARNING")
        self.stdout.info(f'INFO: Loaded workspace (left) from "{ws_path_1}". Time taken: {t.interval:.3f}s.')
        with Timer() as t:
            self.model_2 = ExtendedModel(ws_path_2, data_name=None, verbosity="WARNING")
        self.stdout.info(f'INFO: Loaded workspace (right) from "{ws_path_2}". Time taken: {t.interval:.3f}s.')
        
    def _parse_items(self, items:Optional[Union[List[str], List[WSItem], WSItem, str]]=None) -> List[WSItem]:
        if items is None:
            parsed_items = list(self.kDefaultItems)
        elif isinstance(items, str):
            item = WSItem.parse(items)
            parsed_items = [item]
        elif isinstance(items, WSItem):
            parsed_items = [items]
        elif isinstance(items, list):
            parsed_items = [WSItem.parse(i) for i in items]
        else:
            raise ValueError(f"invalid item format for workspace comparison: {items}")
        return parsed_items
    
    def set_item_content(self, item_type:Union[str, WSItemType], content:int):
        item_type = WSItemType.parse(item_type)
        self.item_contents[item_type] = content
        
    def set_item_style(self, item_type:Union[str, WSItemType], style:int):
        item_type = WSItemType.parse(item_type)
        self.item_styles[item_type] = style
        
    def clear_data(self):
        self.data = {}
        
    def load_data(self, items:Optional[Union[List[str], List[WSItem], WSItem, str]]=None):
        
        if items is None:
            items = self.target_items
        else:
            items = self._parse_items(items)
            self.target_items = items
            
        if any(item.item_type == WSItemType.VARIABLE for item in items):
            for _item in [WSItem.PDF, WSItem.FUNCTION]:
                if _item not in items:
                    self.stdout.info(f'INFO: Added "{_item.title}" to the requested data pool needed for '
                                     'inferring renamed and redefined variables.')
                    items.append(_item)
        
        self.clear_data()
        self.stdout.info("INFO: Loading workspace information...")
        with Timer() as t:
            for item in items:
                item_name = item.name.lower()
                self.data[item_name] = self.get_item_data(item)
        self.stdout.info(f"INFO: All requested data have been successfully loaded. Time taken: {t.interval:.3f}s.")        

    def _get_workspace_data(self):
        item = WSItem.WORKSPACE
        data = ComparisonData.from_WSItem(item)
        ws_name_1 = self.model_1.workspace.GetName()
        ws_name_2 = self.model_2.workspace.GetName()
        data.add_single(name_1=ws_name_1, name_2=ws_name_2)
        return data
    
    def _get_category_data(self):
        item = WSItem.CATEGORY
        data = ComparisonData.from_WSItem(item)
        category_map_1 = self.model_1.get_category_map()
        category_map_2 = self.model_2.get_category_map()
        for category in category_map_1:
            category_map = category_map_1[category]
            definition = self.model_1._format_category_summary(category, category_map)
            data.add_single(name_1=category, definition_1=definition)
        for category in category_map_2:
            category_map = category_map_2[category]
            definition = self.model_2._format_category_summary(category, category_map)
            data.add_single(name_2=category, definition_2=definition)
        return data
    
    def _get_snapshot_data(self):
        item = WSItem.SNAPSHOT
        data = ComparisonData.from_WSItem(item)
        if (quickstats.root_version >= (6, 26, 0)):
            snapshots_1 = self.model_1.workspace.getSnapshots()
            snapshots_2 = self.model_2.workspace.getSnapshots()
            for snapshot in snapshots_1:
                data.add_single(name_1=snapshot.GetName())
            for snapshot in snapshots_2:
                data.add_single(name_2=snapshot.GetName())
        else:
            self.stdout.warning("WARNING: Snapshot listing is only available after ROOT 6.26/00")
        return data
     
    def _get_dataset_data(self):
        item = WSItem.DATASET
        data = ComparisonData.from_WSItem(item)
        datasets_1 = self.model_1.workspace.allData()
        datasets_2 = self.model_2.workspace.allData()
        for dataset in datasets_1:
            data.add_single(name_1=dataset.GetName())
        for dataset in datasets_2:
            data.add_single(name_2=dataset.GetName())
        return data
    
    def _get_pdf_data(self):
        item = WSItem.PDF
        components_1 = self.model_1.workspace.allPdfs()
        components_2 = self.model_2.workspace.allPdfs()
        data = self._get_argset_item_data(item, components_1, components_2)
        return data
    
    def _get_function_data(self):
        item = WSItem.FUNCTION
        components_1 = self.model_1.workspace.allFunctions()
        components_2 = self.model_2.workspace.allFunctions()
        data = self._get_argset_item_data(item, components_1, components_2)
        return data
    
    def _get_variable_data(self, item:WSItem):
        if item.item_type != WSItemType.VARIABLE:
            raise ValueError("item type must be variable")
        variable = item.var_repr
        components_1 = self.model_1.get_variables(variable)
        components_2 = self.model_2.get_variables(variable)
        data = self._get_argset_item_data(item, components_1, components_2)
        return data
    
    def _get_argset_item_data(self, item:WSItem, components_1:ROOT.RooArgSet, components_2:ROOT.RooArgSet):
        data = ComparisonData.from_WSItem(item)
        content = self.item_contents[item.item_type]
        style   = self.item_styles[item.item_type]
        data_1 = get_str_data(components_1, fill_classes=True,
                              fill_definitions=True,
                              content=content, style=style, fmt="dataframe")
        data_2 = get_str_data(components_2, fill_classes=True,
                              fill_definitions=True,
                              content=content, style=style, fmt="dataframe")
        data.add(data_1, data_2)
        return data
    
    def get_item_data(self, item:Union[str, WSItem]):
        item = WSItem.parse(item)
        title = item.title
        self.stdout.info(f'INFO: Retrieving information for the item: "{title}"')
        if item == WSItem.WORKSPACE:
            data = self._get_workspace_data()
        elif item == WSItem.CATEGORY:
            data = self._get_category_data()
        elif item == WSItem.SNAPSHOT:
            data = self._get_snapshot_data()
        elif item == WSItem.DATASET:
            data = self._get_dataset_data()
        elif item == WSItem.PDF:
            data = self._get_pdf_data()
        elif item == WSItem.FUNCTION:
            data = self._get_function_data()
        elif item.item_type == WSItemType.VARIABLE:
            data = self._get_variable_data(item)
        else:
            raise RuntimeError(f"unsupported item type: {item}")
        data.process()
        return data
  
    @staticmethod
    def _dataset_distribution_is_equal(dist_1:Dict, dist_2:Dict):
        categories_1 = dist_1.keys()
        categories_2 = dist_2.keys()
        if set(categories_1) != set(categories_2):
            return False
        for category in categories_1:
            x_1 = dist_1[category]['x']
            x_2 = dist_2[category]['x']
            y_1 = dist_1[category]['y']
            y_2 = dist_2[category]['y']
            if (not np.allclose(x_1, x_2)) or (not np.allclose(y_1, y_2)):
                return False
        return True
    
    def _get_dataset_dist(self, name_1:Optional[str]=None, name_2:Optional[str]=None):
        if name_1 is not None:
            dataset_1 = self.model_1.workspace.data(name_1)
            dist_1 = self.model_1.get_dataset_distributions(dataset_1)
        else:
            dist_1 = None
        if name_2 is not None:
            dataset_2 = self.model_2.workspace.data(name_2)
            dist_2 = self.model_2.get_dataset_distributions(dataset_2)
        else:
            dist_2 = None
        return dist_1, dist_2

    def _process_workspace_data(self):
        item = WSItem.WORKSPACE
        item_name = item.name.lower()
        if item_name not in self.data:
            return None
        data = self.data[item_name]
        df_common = data.get_df("common")
        if len(df_common) == 0:
            df = data.df_merge
            index_1 = df["_merge"] == "left_only"
            index_2 = df["_merge"] == "right_only"
            names_1 = df[index_1]['name'].values
            names_2 = df[index_2]['name'].values
            if (len(names_1) != 1) or (len(names_2) != 1):
                raise RuntimeError("found multiple left/right workspaces in the comparison data")
            df.loc[index_1, ['category']] = "renamed"
            df.loc[index_2, ['category']] = "renamed"
            df.loc[index_1, ['name_alt']] = names_2[0]
            df.loc[index_2, ['name_alt']] = names_1[0]
    
    def _process_dataset_data(self):
        item = WSItem.DATASET
        item_name = item.name.lower()
        self.stdout.info(f'INFO: Processing dataset definitions...')
        if item_name not in self.data:
            self.stdout.warning("WARNING: Dataset data not loaded. Skipping.")
            return None
        with Timer() as t:
            data = self.data[item_name]
            common_dataset_names = data.get_df("common")['name'].values
            dataset_names_1 = data.get_df("left_only")['name'].values
            dataset_names_2 = data.get_df("right_only")['name'].values
            df = data.df_merge
            df.set_index("name", inplace=True)
            for ds_name in common_dataset_names:
                dist_1, dist_2 = self._get_dataset_dist(ds_name, ds_name)
                same_definition = self._dataset_distribution_is_equal(dist_1, dist_2)
                if not same_definition:
                    df.loc[ds_name, ['category']] = "redefined"
            for ds_name_1 in dataset_names_1:
                candidates = []
                dist_1, _ = self._get_dataset_dist(ds_name_1, None)
                for ds_name_2 in dataset_names_2:
                    _, dist_2 = self._get_dataset_dist(None, ds_name_2)
                    same_definition = self._dataset_distribution_is_equal(dist_1, dist_2)
                    if same_definition:
                        candidates.append(ds_name_2)
                # renamed dataset
                if len(candidates) == 1:
                    ds_name_2 = candidates[0]
                    df.loc[ds_name_1, ['category']] = "renamed"
                    df.loc[ds_name_1, ['name_alt']] = ds_name_2
                    df.loc[ds_name_2, ['category']] = "renamed"
                    df.loc[ds_name_2, ['name_alt']] = ds_name_1
            df.reset_index(inplace=True)
        self.stdout.info(f"INFO: Processing finished. Time taken: {t.interval:.3f}s.")
        
    def _get_combined_mapping_statistics(self):
        pdf_item_name = WSItem.PDF.name.lower()
        function_item_name = WSItem.FUNCTION.name.lower()
        items_to_request = []
        if pdf_item_name not in self.data:
            items_to_request.append(WSItem.PDF)
        if function_item_name not in self.data:
            items_to_request.append(WSItem.FUNCTION)
        
        if len(items_to_request) > 0:
            with Timer() as t:
                for item in items_to_request:
                    self.stdout.info(f'INFO: Added "{item.title}" to the requested data pool needed for '
                                     'inferring renamed and redefined variables.')
                    item_name = item.name.lower()
                    self.data[item_name] = self.get_item_data(item)
            self.stdout.info(f"INFO: All requested data have been successfully loaded. Time taken: {t.interval:.3f}s.")
            return self._get_combined_mapping_statistics()
        
        mapping_statistics_pdf = self.data[pdf_item_name].mapping_statistics
        mapping_statistics_function = self.data[function_item_name].mapping_statistics
        combined_mapping = ComparisonData._get_combined_mapping_statistics([mapping_statistics_pdf,
                                                                            mapping_statistics_function])
        return combined_mapping
    
    def _get_items_with_definition(self):
        relevant_items = []
        for item_str in self.data:
            item = WSItem.parse(item_str)
            if item.item_type in [WSItemType.PDF, WSItemType.FUNCTION, WSItemType.VARIABLE]:
                relevant_items.append(item_str)
        return relevant_items

    def _process_renamed_and_remapped_variables(self):
        
        relevant_items = self._get_items_with_definition()
                
        if len(relevant_items) > 0:
            self.stdout.info("INFO: Processing renamed and remapped variables...")
            with Timer() as t:
                combined_mapping_statistics = self._get_combined_mapping_statistics()
                valid_mappings = {}
                for name_1 in combined_mapping_statistics:
                    statistics = combined_mapping_statistics[name_1]
                    candidates = statistics["candidates"]
                    if len(candidates) == 1:
                        name_2 = candidates[0]
                        valid_mappings[name_1] = name_2
                for item_str in relevant_items:
                    data = self.data[item_str]
                    data.process_mappings(valid_mappings)
            self.stdout.info(f"INFO: Processing finished. Time taken: {t.interval:.3f}s")
 
    def process_data(self):
        self._process_workspace_data()
        dataset_item_str = WSItem.DATASET.name.lower()
        if dataset_item_str in self.data:
            self._process_dataset_data()
        self._process_renamed_and_remapped_variables()
    
    def _get_definition_map(self):
        relevant_items = self._get_items_with_definition()
        definition_map = {}
        for item_str in relevant_items:
            data = self.data[item_str]
            df = data.get_df("right")
            names = df['name'].values
            definitions = df['definition_right'].values
            def_map = dict(zip(names, definitions))
            definition_map.update(def_map)
        return definition_map
    
    def get_summary_str(self, indent:str="   "):
        definition_map = self._get_definition_map()
        combined_summary_str = ""
        for item_str, data in self.data.items():
            if data.df_merge is None:
                continue
            item = WSItem.parse(item_str)
            if item not in self.target_items:
                continue
            visibility = self.visibility_map.get(item_str, item.default_visibility)
            summary_str = data.get_summary_str(visibility=visibility,
                                               ext_ref=definition_map,
                                               indent=indent)
            combined_summary_str += summary_str
        return combined_summary_str
    
    def print_summary(self, indent:str="   "):
        summary_str = self.get_summary_str(indent=indent)
        self.stdout.info(summary_str)
        
    @classmethod
    def from_json(cls, filename:str):
        with open(filename, "r") as infile:
            json_data = json.load(infile)
        instance = cls()
        items = []
        import pandas as pd
        for item_str, data in json_data.items():
            item = WSItem.parse(item_str)
            items.append(item)
            df = pd.DataFrame(data)
            instance.data[item_str] = ComparisonData.from_dataframe(item, df)
        instance.target_items = items
        return instance
    
    @classmethod
    def from_excel(cls, filename:str):
        import pandas as pd
        instance = cls()
        excel_data = pd.read_excel(filename, sheet_name=None)
        items = []
        for item_str, df in excel_data.items():
            item = WSItem.parse(item_str)
            items.append(item)
            instance.data[item_str] = ComparisonData.from_dataframe(item, df)
        instance.target_items = items
        return instance
    
    def save_json(self, filename:str):
        json_data = {}
        self.stdout.info(f'INFO: Saving comparison result in json format as "{filename}"...')
        for item_str, data in self.data.items():
            if data.df_merge is None:
                data.process()
            # only save items that are requested
            item = WSItem.parse(item_str)
            if item in self.target_items:
                json_data[item_str] = data.df_merge.to_dict('records')
        with open(filename, "w") as outfile:
            json.dump(json_data, outfile, indent=2)
    
    def save_excel(self, filename:str):
        self.stdout.info(f'INFO: Saving comparison result in excel format as "{filename}"...')
        import pandas as pd
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        for item_str, data in self.data.items():
            if data.df_merge is None:
                data.process()
            # only save items that are requested
            item = WSItem.parse(item_str)
            df = data.df_merge
            df.to_excel(writer, sheet_name=item_str, index=False)
        writer.save()