#!/usr/bin/env python3
"""
Ageas Reborn
Generate pseudo-cell GRNs (pcGRNs) from GEMs

author: jy, nkmtmsys

ToDo:
__file_method not done at all
gem_data method also need to be done <- higher priority
"""

import os
import statistics as sta
import ageas.tool as tool
import ageas.tool.gem as gem
import ageas.tool.json as json
from scipy.stats import pearsonr



class Make:
    """
    Make grns for gene expression datas
    """
    def __init__(self,
                database_info = None,
                std_value_thread = None,
                std_ratio_thread = None,
                correlation_thread = 0.2,
                gem_data = None,
                meta_grn = None,
                load_path = None):
        super(Make, self).__init__()
        # Initialize
        self.database_info = database_info
        self.std_value_thread = std_value_thread
        self.std_ratio_thread = std_ratio_thread
        self.correlation_thread = correlation_thread
        if self.correlation_thread is None: self.correlation_thread = 0
        # load in
        if load_path is not None:
            self.class1_pcGRNs,self.class2_pcGRNs=self.__load_pcGRNs(load_path)
        # Make GRNs
        else:
            self.class1_pcGRNs,self.class2_pcGRNs=self.__make_pcGRNs(gem_data,
                                                                    meta_grn)

    # main controller to cast pseudo cell GRNs (pcGRNs)
    def __make_pcGRNs(self, gem_data, meta_grn):
        if gem_data is not None:
            class1_pcGRNs = self.__loaded_gem_method(gem_data.class1, meta_grn)
            class2_pcGRNs = self.__loaded_gem_method(gem_data.class2, meta_grn)
        elif self.database_info.type == 'gem_folder':
            class1_pcGRNs = self.__folder_method(self.database_info.class1_path,
                                                meta_grn)
            class2_pcGRNs = self.__folder_method(self.database_info.class2_path,
                                                meta_grn)
        elif self.database_info.type == 'gem_file':
            # need to revise here!
            class1_pcGRNs = self.__file_method(self.database_info.class1_path,
                                                meta_grn)
            class2_pcGRNs = self.__file_method(self.database_info.class2_path,
                                                meta_grn)
        else:
            raise tool.Error('pcGRN Caster Error: Unsupported database type')
        return class1_pcGRNs, class2_pcGRNs

    # as named
    def __file_method(self, path, meta_grn):
        pcGRNs = {}
        print('pcgrn_caster.py:class Make: need to do something here')
        return pcGRNs

    # as named
    def __loaded_gem_method(self, gem, meta_grn):
        pcGRNs = {}
        sample_num = 0
        start = 0
        end = self.database_info.sliding_window_size
        # set stride
        if self.database_info.sliding_window_stride is not None:
            stride = self.database_info.sliding_window_stride
        else:
            stride = end
        # use sliding window techinque to set pseudo cell
        loop = True
        while loop:
            if start >= len(gem.columns):
                break
            elif end >= len(gem.columns):
                end = len(gem.columns)
                loop = False
            sample_id = 'sample' + str(sample_num)
            sample = gem.iloc[:, start:end]
            if meta_grn is not None:
                grn = self.__process_sample_with_metaGRN(sample, meta_grn)
            else:
                grn = self.__process_sample_without_guidance(sample)
            # Save data into pcGRNs
            pcGRNs[sample_id] = self.__reform_grn(grn)
            start += stride
            end += stride
            sample_num += 1
        return pcGRNs

    # as named
    def __folder_method(self, path, meta_grn):
        data = self.__readin_folder(path)
        pcGRNs = {}
        for sample in data:
            if meta_grn is not None:
                grn = self.__process_sample_with_metaGRN(data[sample], meta_grn)
            else:
                grn = self.__process_sample_without_guidance(data[sample])
            # Save data into pcGRNs
            pcGRNs[sample] = self.__reform_grn(grn)
        return pcGRNs

    # again, as named
    def __reform_grn(self, grn):
        return {pth:data for pth,data in grn.items() if data is not None}

    # as named
    def __process_sample_with_metaGRN(self, gem, meta_grn):
        grn = {}
        for grp in meta_grn['grps']:
            source_ID = meta_grn['grps'][grp]['regulatory_source']
            target_ID = meta_grn['grps'][grp]['regulatory_target']
            try:
                source_exp = list(gem.loc[[source_ID]].values[0])
                target_exp = list(gem.loc[[target_ID]].values[0])
            except:
                continue
            # No need to compute if one array is constant
            if len(set(source_exp)) == 1 or len(set(target_exp)) == 1:
                continue
            cor = pearsonr(source_exp, target_exp)[0]
            if abs(cor) > self.correlation_thread:
                grn[grp] = {
                    'id': grp,
                    'regulatory_source': source_ID,
                    'source_expression_mean': float(sta.mean(source_exp)),
                    'regulatory_target': target_ID,
                    'target_expression_mean': float(sta.mean(target_exp)),
                    'correlation':cor
                }
        return grn

    # Process data without guidance
    # May need to revise later
    def __process_sample_without_guidance(self, gem):
        grn = {}
        # Get source TF
        for source_ID in gem.index:
            # Get target gene
            for target_ID in gem.index:
                if source_ID == target_ID:
                    continue
                grp = tool.Cast_GRP_ID(source_ID, target_ID)
                if grp not in grn:
                    # No need to compute if one array is constant
                    s_exp = gem[source_ID]
                    t_exp = gem[target_ID]
                    if len(set(s_exp)) == 1 or len(set(t_exp)) == 1: continue
                    cor = pearsonr(s_exp, t_exp)[0]
                    if abs(cor) > self.correlation_thread:
                        grn[grp] = {
                            'id': grp,
                            'regulatory_source': source_ID,
                            'source_expression_mean': float(sta.mean(s_exp)),
                            'regulatory_target': target_ID,
                            'target_expression_mean': float(sta.mean(t_exp)),
                            'correlation':cor
                        }
                    else:
                        grn[grp] = None
        return grn

    # Readin Gene Expression Matrices in given class path
    def __readin_folder(self, path):
        result = {}
        for filename in os.listdir(path):
            filename = path + '/' + filename
            # read in GEM files
            temp = gem.Reader(filename, header = 0, index_col = 0)
            temp.STD_Filter(std_value_thread = self.std_value_thread,
                            std_ratio_thread = self.std_ratio_thread)
            result[filename] = temp.data
        return result

    # as named
    def update_with_remove_list(self, remove_list):
        for sample in self.class1_pcGRNs:
            for id in remove_list:
                if id in self.class1_pcGRNs[sample]:
                    del self.class1_pcGRNs[sample][id]
        for sample in self.class2_pcGRNs:
            for id in remove_list:
                if id in self.class2_pcGRNs[sample]:
                    del self.class2_pcGRNs[sample][id]

    # temporal pcGRN saving method
    """ need to be revised later to save pcGRNs file by file"""
    def save(self, save_path):
        json.encode({'class1':self.class1_pcGRNs, 'class2':self.class2_pcGRNs},
                    save_path)

    # load in pcGRNs from files
    """ need to be revised later with save_pcGRNs"""
    def __load_pcGRNs(self, load_path):
        data = json.decode(load_path)
        return data['class1'], data['class2']



    # OLD: Save GRN files as js.gz in new folder
    # def save_GRN(self, data, save_path):
    #     for sample in data:
    #         names = sample.strip().split('/')
    #         name = names[-1].split('.')[0] + '.js'
    #         path = '/'.join(names[:-3] + [save_path, names[-2], name])
    #         # Make dir if dir not exists
    #         folder = os.path.dirname(path)
    #         if not os.path.exists(folder):
    #             os.makedirs(folder)
    #         # Get GRN and save it
    #         grn = data[sample]
    #         json.encode(grn, out = path)
