#!/usr/bin/env python3
"""
Pack bioGRID data into .json based format with necessary data

author: jy, nkmtmsys
"""


import os
import pandas as pd
import ageas.tool as tool
import ageas.tool.json as json



class Processor:
    """
    Process summarized bioGRID file
    """
    def __init__(self, specie_path, path = 'bioGRiD_stratified.js.gz'):
        self.path = specie_path + path
        data = json.decode(self.path)
        self.alias = data['alias']
        self.data = data['interactions']



class Reader(tool.Reader_Template):
    def __init__(self,
                filepath: str,
                organism_a_id: str = '10090', # human is 9606, mouse is 10090
                organism_b_id = None):
        if organism_b_id is None:
            organism_b_id = organism_a_id
        self.load(filepath)
        self.dict = self._process(org_a = organism_a_id, org_b = organism_b_id)

    def _process(self, org_a = None, org_b = None):
        result = {
            'alias':{},
            'interactions':{}
        }
        # skip headers
        while(True):
            line = self.file.readline()
            if line[:12] == 'INTERACTOR_A':  break
        # now we read in records
        while(True):
            line = self.file.readline()
            if line == '': break
            content = line.split('\t')
            assert len(content) == 11
            if content[-2].strip() == org_a and content[-1].strip() == org_b:
                geneA = content[2].upper()
                geneB = content[3].upper()
                geneA_alias = content[4].upper()
                geneB_alias = content[5].upper()
                self.__update_interactions(geneA, geneB, result['interactions'])
                self.__update_interactions(geneB, geneA, result['interactions'])
                self.__update_alias(geneA, geneA_alias, result['alias'])
                self.__update_alias(geneB, geneB_alias, result['alias'])
        return result

    def __update_interactions(self, key, target, dict):
        if key in dict and target not in dict[key]:
            dict[key].append(target)
        elif key not in dict:
            dict[key] = [target]

    def __update_alias(self, gene, alias, dict):
        if alias == '-': return
        all_names = alias.split('|')
        for name in all_names:
            if name not in dict:
                dict[name] = [gene]
            else:
                if gene not in dict[name]:
                    dict[name].append(gene)

    def save(self, outpath):
        json.encode(self.dict, outpath)

""" For example """
# if __name__ == '__main__':
#     a = Reader(filepath = 'BIOGRID-ALL-4.4.203.tab.txt')
#     a.save('bioGRiD_stratified.js.gz')
