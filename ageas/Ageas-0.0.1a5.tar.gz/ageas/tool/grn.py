#!/usr/bin/env python3
"""
GRN related tools

author: jy, nkmtmsys
"""

import re
import statistics as sta
import ageas.tool as tool



class Reader(tool.Reader_Template):
	"""
	Class to read in scRNA-seq or bulk RNA-seq based Gene Expression Matrices
	Only suppordt .cvs and .txt for now
	"""
	def __init__(self, filename, skipFirst = False, stdevThread = None):
		super(Reader, self).__init__()
		# Initialization
		self.load(filename)
		self.entryCoords = {}
		self.iteration = 0
		# Determine file type
		if re.search(r'\.txt', self.filePath): self.split = '\t'
		elif re.search(r'\.csv', self.filePath): self.split = ','
		else: raise tool.Error(self.filePath, ' is not supported format')
		# Skip first line
		if skipFirst: line = self.file.readline()
		# Iterate through all lines
		while(True):
			coordinate = self.file.tell()
			line = self.file.readline().strip()
			# terminate at the end
			if line == '':break
			# skip comments
			elif line[:1] == '#': continue
			else:
				content = line.split(self.split)
				self._processLine(coordinate, content, stdevThread)

	# Process information in reading line
	def _processLine(self, coordinate, content, stdevThread):
		# Check file format
		if len(content) < 7:
			if content == ['\n']:
				raise tool.Error('Bad GRN format: empty line')
			else:
				raise tool.Error('Fatal GRN format: not enough info')
		# Process current record
		else:
			id = content[0]
			if id not in self.entryCoords:
				self.entryCoords[id] = coordinate
			else:
				raise tool.Error('Dulpicate GRP id in GRN: ' + self.filePath)

	# Pattern info in each line
	def _prepareInfo(self, content):
		return {'id':content[0],
				'regulatory_source':content[1],
				'sourceGroup':content[2],
				'regulatory_target':content[3],
				'targetGroup':content[4],
				'correlation':float(content[5]),
				'attribute':content[6],}

	# Output all Gene Expression data in dict format
	def makeGeneExpDict(self, stdevKpRatio):
		records = []
		for id in self.entryCoords:
			_, data = self.get(id)
			if stdevKpRatio is not None:
				stdev = sta.stdev(data)
				records.append([id, stdev, data])
			else:
				records.append([id, data])
		# Filter records based on keep ratio
		if stdevKpRatio is not None:
			records.sort(key = lambda x:x[1], reverse = True)
			records = records[:int(len(records) * stdevKpRatio)]
		return {record[0]: record[-1] for record in records}

	# Get info of selected id
	def get(self, id):
		self.file.seek(self.entryCoords[id])
		line = self.file.readline().strip()
		content = line.split(self.split)
		return self._prepareInfo(content)

	# For iteration
	def __next__(self):
		entryKeys = [*self.entryCoords]
		if self.iteration == len(entryKeys):
			self.iteration = 0
			raise StopIteration
		else:
			id = entryKeys[self.iteration]
			self.iteration += 1
			return self.get(self, id)


	""" Old GEM Reader """
	# # Pattern info in each line
	# def _prepareInfo(self, content):
	#     id = content[0].strip().upper()
	#     data = [float(x) for x in content[1:]]
	#     return id, data
	#
	# # Process information in reading line
	# def _processLine(self, coordinate, content, stdevThread):
	# 	id, data = self._prepareInfo(content)
	# 	stdev = sta.stdev(data)
	# 	# Filter records based on stdev thredshould
	# 	if stdevThread is None or stdev >= stdevThread:
	# 		if id not in self.entryCoords:
	# 			self.entryCoords[id] = coordinate
	# 		# Keep one with high stdev
	# 		else:
	# 			message = id + 'is duplicated'
	# 			warn(message)
	# 			if stdev > sta.stdev(self.get(id)[1]):
	# 				self.entryCoords[id] = coordinate
	# 			# get back to original position
	# 			self.file.seek(coordinate)
	# 			line = self.file.readline().strip()
