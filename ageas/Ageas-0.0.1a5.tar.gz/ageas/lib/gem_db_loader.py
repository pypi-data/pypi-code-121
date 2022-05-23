#!/usr/bin/env python3
"""
Ageas Reborn

author: jy, nkmtmsys
"""

import re
import pandas as pd
import ageas.tool as tool
import ageas.tool.gem as gem
import ageas.tool.json as json
import ageas.tool.gtrd as gtrd
import ageas.tool.biogrid as biogrid
import ageas.lib as lib
import ageas.tool.transfac as transfac
from ageas.lib.deg_finder import Find
from ageas.database_setup import get_specie_path



class Load:
    """
    Load in GEM data sets
    """
    def __init__(self,
                database_info,
                mww_thread = 0.05,
                log2fc_thread = 0.1,
                std_value_thread = 100,
                std_ratio_thread = None):
        super(Load, self).__init__()
        # Initialization
        self.database_info = database_info
        # Load TF databases based on specie
        specie = get_specie_path(__name__, self.database_info.specie)
        # Load TRANSFAC databases
        self.tf_list = transfac.Reader(specie + 'Tranfac201803_MotifTFsF.txt',
                                        self.database_info.factor_name_type).tfs
        # Load interaction database
        if self.database_info.interaction_db == 'gtrd':
            self.interactions = gtrd.Processor(specie,
                                            self.database_info.factor_name_type,
                                            path = 'wholeGene.js.gz')
        elif self.database_info.interaction_db == 'biogrid':
            assert self.database_info.factor_name_type == 'gene_name'
            self.interactions = biogrid.Processor(specie_path = specie)
        # process file or folder based on database type
        if self.database_info.type == 'gem_folder':
            class1, class2 = self.__process_gem_folder(std_value_thread,
                                                        std_ratio_thread)
        elif self.database_info.type == 'gem_file':
            class1, class2 = self.__process_gem_file(std_value_thread,
                                                        std_ratio_thread)
        # Distribuition Filter if threshod is specified
        if mww_thread is not None or log2fc_thread is not None:
            self.genes = Find(class1,
                                class2,
                                mww_thread = mww_thread,
                                log2fc_thread = log2fc_thread).degs
            self.class1 = class1.loc[class1.index.intersection(self.genes)]
            self.class2 = class2.loc[class2.index.intersection(self.genes)]
        else:
            self.genes = class1.index.union(class2.index)
            self.class1 = class1
            self.class2 = class2


    # Process in expression matrix file (dataframe) scenario
    def __process_gem_file(self, std_value_thread, std_ratio_thread):
        class1 = self.__read_df(self.database_info.class1_path,
                                std_value_thread,
                                std_ratio_thread)
        class2 = self.__read_df(self.database_info.class2_path,
                                std_value_thread,
                                std_ratio_thread)
        return class1, class2

    # Read in gem file
    def __read_df(self, path, std_value_thread, std_ratio_thread):
        # Decide which seperation mark to use
        if re.search(r'csv', path): sep = ','
        elif re.search(r'txt', path): sep = '\t'
        else: raise lib.Error('Unsupported File Type: ', path)
        # Decide which compression method to use
        if re.search(r'.gz', path): compression = 'gzip'
        else: compression = 'infer'
        df = pd.read_csv(path,
                        sep = sep,
                        compression = compression,
                        header = 0,
                        index_col = 0)
        return tool.STD_Filter(df, std_value_thread, std_ratio_thread)

    # Process in Database scenario
    def __process_gem_folder(self, std_value_thread, std_ratio_thread):
        class1 = gem.Folder(self.database_info.class1_path).combine(
                                            std_value_thread = std_value_thread,
                                            std_ratio_thread = std_ratio_thread)
        class2 = gem.Folder(self.database_info.class2_path).combine(
                                            std_value_thread = std_value_thread,
                                            std_ratio_thread = std_ratio_thread)
        return class1, class2
