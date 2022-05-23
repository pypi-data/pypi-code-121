#!/usr/bin/env python3
"""
Uniprot ID Map related tools

author: jy, nkmtmsys
"""

import ageas.tool as tool
import ageas.tool.json as json



def Process(datapath, factor_name_type):
    if factor_name_type == 'gene_name':
        return json.decode(datapath + 'GSName2UniID.js.gz')
    elif factor_name_type == 'ens_id':
        return json.decode(datapath + 'ENS2UniID.js.gz')
    else: raise tool.Error(factor_name_type, ' such id is not supported yet!')



class Reader(tool.Reader_Template):
    """
    Read in ID Map file obtained from Uniprot
    """
    def __init__(self, filename):
        super(Reader, self).__init__()
        self.load(filename)

    # Stratify the map file with selected genra -> Genra: Uniprot ID
    def stratify(self, genra = ['Gene_Name', 'Gene_Synonym']):
        result = {}
        while(True):
            line = self.file.readline()
            if line == '': break
            elif line[:1] == '#': continue
            content = line.split('\t')
            if content[1] in genra:
                name = content[2].strip().upper()
                uniID = content[0].strip().upper()
                if name in result:
                    result[name] += ';'+uniID
                else:
                    result[name] = uniID
        return result
