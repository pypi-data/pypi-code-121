#!/usr/bin/env python3
"""
Pack GTRD data into .json based format with necessary data

ToDo:
Make sure load all tf target info at once would still be fine


author: jy, nkmtmsys
"""


import os
import pandas as pd
import ageas.tool as tool
import ageas.tool.json as json
import ageas.tool.uniprot_id_map as uniprot_id_map



class Processor:
    """
    Process summarized GTRD file
    """
    def __init__(self, specie_path, factor_name_type, path):
        self.path = specie_path + path
        self.nameType = factor_name_type
        self.idmap = uniprot_id_map.Process(specie_path, factor_name_type)
        self.data = json.decode(self.path)



class Packer:
    def __init__(self, database_path, outpath = None):
        self.dict = {}
        filenames = os.listdir(database_path)
        for ele in filenames:
            tf = ele.split('.txt')[0].upper()
            if tf not in self.dict:
                self.dict[tf] = self._processGene(database_path + '/' + ele,
                                                        sep = "\t",
                                                        header = 0)
            else: raise tool.Error('Duplicated TF file in:', database_path)
        if outpath is None: return
        else: json.encode(self.dict, outpath)

    def _processFull(self, filepath, sep, header):
        result = {}
        tarTable = pd.read_csv(filepath, sep = sep, header = header)
        for index, row in tarTable.iterrows():
            result[row['Gene symbol'].upper()] = {
                'id':row['id'],
                'ENS_TransID':row['Ensembl ID'],
                'siteCount':row['SiteCount']
            }
        return result

    def _processGene(self, filepath, sep, header):
        tarTable = pd.read_csv(filepath, sep = sep, header = header)
        return dict(zip(tarTable['Gene symbol'].str.upper(),
                        tarTable['SiteCount']))
