#!/usr/bin/env python3
"""
Read in MEX format Single Cell Expression Data

author: jy, nkmtmsys
"""
import os
import re
import csv
import gzip
import scipy.io
import pandas as pd
from warnings import warn
import ageas.tool.gem as gem



class Reader(gem.Reader):
    """
    Read in MEX data for Gene expression information
    """

    def __init__(self,
                matrix_path:str = None,
                features_path:str = None,
                barcodes_path:str = None):
        self.matrix_path = matrix_path
        self.features_path = features_path
        self.barcodes_path = barcodes_path
        self.data = pd.DataFrame(scipy.io.mmread(self.matrix_path).toarray())
        self.features = csv.reader(gzip.open(self.features_path,'rt'),
                                            delimiter = '\t')
        self.barcodes = csv.reader(gzip.open(self.barcodes_path, 'rt'),
                                            delimiter = '\t')

    def get_gem(self, gene_id_type:int = 1, save_path:str = None):
    	self.data.index = [x.upper() for x in [y[gene_id_type]
                                        for y in self.features]]
    	self.data.columns = [row[-1] for row in self.barcodes]
        # sum up data sharing same gene name if any
    	if len(self.data.columns) != len(list(set(self.data.columns))):
            warn('Found repeated barcodes in', self.barcodes_path, ' Merging.')
    		self.data = self.data.groupby(self.data.columns).sum()
        # summ up data sharing same barcode if any
    	if len(self.data.index) != len(list(set(self.data.index))):
            warn('Found repeated genes in', self.features_path, ' Merging.')
    		self.data = self.data.groupby(self.data.index).sum()
        # assertion part
    	assert len(self.data.columns) == len(list(set(self.data.columns)))
    	assert len(self.data.index) == len(list(set(self.data.index)))
    	# save GEM if specified path to save
    	if save_path is not None: self.data.to_csv(save_path)
    	return self.data
