#!/usr/bin/env python3
"""
Ageas Reborn
Gene Expression Matrix related tools

ToDo: make SQL Database based on folder/file
Find a way to deal with seurat objects
author: jy, nkmtmsys
"""

import os
import re
import pandas as pd
import ageas.tool as tool
from warnings import warn



class Reader(object):
	"""
	Class to read in scRNA-seq or bulk RNA-seq based Gene Expression Matrices
	Only suppordt .cvs and .txt for now
	"""
	def __init__(self, path:str = None, **kwargs):
		super(Reader, self).__init__()
		# Decide which seperation mark to use
		if re.search(r'csv', path): 	self.sep = ','
		elif re.search(r'txt', path): 	self.vsep = '\t'
		# determine compression method
		if re.search(r'.gz', path): 	self.compression = 'gzip'
		elif re.search(r'.zip', path):	self.compression = 'zip'
		else: 							self.compression = 'infer'
		try:
			self.data = pd.read_csv(path,
									sep = self.sep,
									compression = self.compression,
									**kwargs)
		except Exception as GEM_Reader_Error:
			raise tool.Error('Unsupported File Type: ', path)

	# filter data frame based on standered deviations
	def STD_Filter(self, std_value_thread = None, std_ratio_thread = None):
		self.data = tool.STD_Filter(df = self.data,
									std_value_thread = std_value_thread,
									std_ratio_thread = std_ratio_thread)



class Folder(object):
	"""
	Manipulations on Gene Expressio Matrices in given folder
	"""
	def __init__(self,
				path:str = None,
				file_type = 'csv', 				# type of file considering GEM
				compression_method = 'infer',	# compression method of files
				header_row = 0, 				# header row for all GEM
				index_col = 0, 					# index column for all GEM
				):
		self.path = path
		self.header_row = header_row
		self.index_col = index_col

		# file type check
		if file_type == 'csv': self.sep = ','
		elif file_type == 'txt': self.sep = '\t'
		else: raise tool.Error('Folder: Unknown file type')
		self.file_type = file_type
		self.compression_method = compression_method

	# combine all GEMs to one unified GEM
	# all GEMs should have exactly same index (Gene list)
	def combine(self,
				method = 'inner',
				keep_repeated_samples = False,
				std_value_thread = None,
				std_ratio_thread = None,
				outpath = None
				):
		# Grab all necessary samples first
		result = None
		for filename in os.listdir(self.path):
			# Skip files without targeting appendix
			if not re.search(self.file_type, filename): continue
			filepath = self.path + '/' + filename
			gem = pd.read_csv(filepath,
								sep = self.sep,
								header = self.header_row,
								index_col = self.index_col,
								compression = self.compression_method)
			# Initialize output df if still empty
			if result is None:
				result = gem
				continue
			if keep_repeated_samples:
				result = result.join(gem, how = method)
			else:
				unique_samples = gem.columns.difference(result.columns)
				# if nothing new, move forward
				if len(unique_samples) == 0: continue
				result = pd.merge(result,
								gem[unique_samples],
								left_index = True,
								right_index = True,
								how = method)
			# Just in case
			result = result[~result.index.duplicated(keep='first')]
		del gem

		# filter by standard deviations if needed
		if std_value_thread is not None or std_ratio_thread is not None:
			result = tool.STD_Filter(result, std_value_thread, std_ratio_thread)

		# return or save matrix
		if outpath is None: return result
		else:
			result.to_csv(outpath,
							sep = self.sep,
							compression = self.compression_method)
