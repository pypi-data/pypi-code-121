#!/usr/bin/env python3
"""
TRANSFAC file related tools

author: jy, nkmtmsys
"""


import re
import ageas.tool as tool

class Reader(tool.Reader_Template):
    """
    Load in Transfac database for RNA-seq based gene expression file readin
    May need to be override if TF database in different format
    """

    def __init__(self, filename, type = 'gene_name'):
        self.load(filename)
        self.tfs = {}
        if type == 'gene_name': self._process(position = 3)
        elif type == 'ens_id': self._process(position = 4)
        else: raise tool.Error('Unsupported factor name type!')
        self.close()

    # Iterate lines of input file
    def _process(self, position):
        while(True):
            line = self.file.readline().strip()
            if line == '':break
            elif line[:1] == '#':continue
            content = line.split('\t')
            self._update(content[position])

    # Update dict with given data
    def _update(self, data):
        if re.search(r';', data):
            data = data.split(';')
            for ele in data: self.tfs[ele.upper()] = ''
        else: self.tfs[data.upper()] = ''
