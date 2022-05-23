#!/usr/bin/env python3
"""
Ageas Reborn

author: jy, nkmtmsys
"""
import math
import itertools
import pandas as pd
import ageas.lib as lib
import ageas.tool as tool
from collections import OrderedDict


TYPES = ['Standard', 'Outer', 'Bridge']


class Extract(object):
	"""
	Extract key genes from the most important GRPs
	"""

	def __init__(self,
				grp_importances = None,
				score_thread = None,
				outlier_grps = {},
				top_grp_amount = None):
		super(Extract, self).__init__()
		self.regulons = []
		self.regulatory_sources = None
		self.outlier_grps = outlier_grps
		self.grps = grp_importances.stratify(score_thread,
											top_grp_amount,
											len(outlier_grps))
	# as named
	def change_regulon_list_to_dict(self, header = 'regulon_'):
		self.regulons = {header + str(i):e for i, e in enumerate(self.regulons)}

	# as named
	def build_regulon(self, meta_grn, impact_depth = 3):
		# set outlier bonus score to max score of standard GRPs
		outlier_bonus_score = self.grps.iloc[0]['importance']
		# process standard grps
		for id in self.grps.index:
			try:
				grp = meta_grn['grps'][id]
			except Exception:
				raise lib.Error('GRP', id, 'not in Meta GRN')
			grp['type'] = TYPES[0]
			grp['score'] = self.grps.loc[id]['importance']
			self.__update_regulon_with_grp(grp)
		for id in self.outlier_grps:
			try:
				grp = meta_grn['grps'][id]
			except Exception:
				raise lib.Error('GRP', id, 'not in Meta GRN')
			grp['type'] = TYPES[1]
			grp['score'] = self.outlier_grps[id] + outlier_bonus_score
			self.__update_regulon_with_grp(grp)

		# combine regulons if sharing common genes
		i = 0
		j = 1
		checked_grps = {}
		while True:
			if i == len(self.regulons) or j == len(self.regulons): break
			combining = False
			reg1_genes = self.regulons[i]['genes'].keys()
			reg2_genes = self.regulons[j]['genes'].keys()
			assert len([x for x in reg1_genes if x in reg2_genes]) == 0
			for comb in list(itertools.product(reg1_genes, reg2_genes)):
				id = tool.Cast_GRP_ID(comb[0], comb[1])
				if id not in checked_grps:
					checked_grps[id] = None
					if id in meta_grn['grps']:
						if not combining: combining = True
						assert id not in self.regulons[i]['grps']
						meta_grn['grps'][id]['type'] = TYPES[2]
						meta_grn['grps'][id]['score'] = 0
						self.regulons[i]['grps'][id] = meta_grn['grps'][id]
			if combining:
				self.__combine_regulons(ind_1 = i, ind_2 = j)
				del self.regulons[j]
				j = i + 1
			else:
				j += 1
				if j == len(self.regulons):
					i += 1
					j = i + 1

		# update and change regulon to dict type and find key genes
		for regulon in self.regulons:
			for grp in regulon['grps'].values():
				source = grp['regulatory_source']
				target = grp['regulatory_target']
				# update genes type based on GRP type
				if grp['type'] == TYPES[1]:
					if regulon['genes'][source]['type'] != TYPES[1]:
						regulon['genes'][source]['type'] = TYPES[1]
					if regulon['genes'][target]['type'] != TYPES[1]:
						regulon['genes'][target]['type'] = TYPES[1]
				elif grp['type'] == TYPES[0]:
					if (regulon['genes'][source]['type'] != TYPES[1] and
						regulon['genes'][source]['type'] != TYPES[0]):
						regulon['genes'][source]['type'] = TYPES[0]
					if (regulon['genes'][target]['type'] != TYPES[1] and
						regulon['genes'][target]['type'] != TYPES[0]):
						regulon['genes'][target]['type'] = TYPES[0]
				self.__update_regulon_gene_list(source = source,
												target = target,
												gene_list = regulon['genes'],
												reversable = grp['reversable'])
		self.regulatory_sources = self.__get_reg_sources(impact_depth)
		del self.grps
		del self.outlier_grps

	# Use extra GRPs from meta GRN to link different Regulons
	def link_regulon(self, meta_grn = None, allowrance = 1):
		# initialize
		grp_skip_list = {}
		for regulon in self.regulons:
			for grp_id in regulon['grps']:
				grp_skip_list[grp_id] = None
		combine_list = []
		for gene in self.regulatory_sources:
			self.__find_bridges_by_gene(gene,
									self.regulatory_sources[gene]['regulon_id'],
									meta_grn,
									allowrance,
									grp_skip_list,
									combine_list,
									[])
		for comb in combine_list:
			assert len(comb[0]) >= 2
			extend_regulon = self.regulons[comb[0][0]]
			for i in range(1, len(comb[0])):
				self.__combine_regulons(ind_1 = comb[0][0], ind_2 = comb[0][i])
				self.regulons[comb[0][i]] = None
			for grp_id in comb[1]:
				# skip if already added
				if grp_id in extend_regulon['grps']: continue
				# update GRP information and add it to regulon
				meta_grn['grps'][grp_id]['type'] = TYPES[2]
				meta_grn['grps'][grp_id]['score'] = 0
				extend_regulon['grps'][grp_id] = meta_grn['grps'][grp_id]
				# update gene list in regulon
				source = meta_grn['grps'][grp_id]['regulatory_source']
				target = meta_grn['grps'][grp_id]['regulatory_target']
				if source not in extend_regulon['genes']:
					extend_regulon['genes'][source] = {'source':[],
														'target':[],
														'type':TYPES[2]}
				if target not in extend_regulon['genes']:
					extend_regulon['genes'][target] = {'source':[],
														'target':[],
														'type':TYPES[2]}
				self.__update_regulon_gene_list(source = source,
							target = target,
							gene_list = extend_regulon['genes'],
							reversable = meta_grn['grps'][grp_id]['reversable'])
		self.regulons = [e for e in self.regulons if e is not None]
		self.regulatory_sources = self.__get_reg_sources()

	# find factors by checking and regulaotry target number and impact score
	def report(self, meta_grn, impact_score_thread = 0):
		df = []
		for k, v in self.regulatory_sources.items():
			if v['impact_score'] >= impact_score_thread:
				exps = meta_grn['mean_gene_expressions'][k]
				fc = abs(math.log2( (exps['class1']+1) / (exps['class2']+1) ))
				df.append([k] + list(v.values()) + [fc])
		df = pd.DataFrame(sorted(df, key=lambda x:x[-1], reverse = True))
		df.columns=['Gene',
					'Regulon',
					'Type',
					'Source_Num',
					'Target_Num',
					'Impact_Score',
					'LogFC']
		return df

	# recursively add up impact score with GRP linking gene to its target
	def  __get_impact_genes(self, regulon, gene, depth, dict):
		if depth > 0:
			depth -= 1
			for target in regulon['genes'][gene]['target']:
				# if regulon['genes'][target]['type'] != TYPES[2]:
				if target not in dict: dict[target] = None
				# score += regulon['grps'][tool.Cast_GRP_ID(gene,target)]['score']
				if len(regulon['genes'][target]['target']) > 0:
					dict = self.__get_impact_genes(regulon, target, depth, dict)
		return dict

	# combine regulons in self.regulons by index
	def __combine_regulons(self, ind_1, ind_2):
		self.regulons[ind_1]['grps'].update(self.regulons[ind_2]['grps'])
		self.regulons[ind_1]['genes'].update(self.regulons[ind_2]['genes'])

	# summarize key regulatory sources appearing in regulons
	def __get_reg_sources(self, impact_depth = 3):
		dict = {}
		for regulon_id, regulon in enumerate(self.regulons):
			for gene in regulon['genes']:
				source_num = len(regulon['genes'][gene]['source'])
				target_num = len(regulon['genes'][gene]['target'])
				if (gene not in dict and
					# regulon['genes'][gene]['type'] != TYPES[2] and
					target_num >= 1):
					impact = self.__get_impact_genes(self.regulons[regulon_id],
													gene,
													impact_depth,
													{})
					dict[gene]= {
									'regulon_id': regulon_id,
									'type':	regulon['genes'][gene]['type'],
									'source_num': source_num,
									'target_num': target_num,
									'impact_score': len(impact)
								}
				elif gene in dict:
					raise lib.Error('Repeated Gene in regulons', gene)
		# filter by top_grp_amount
		return OrderedDict(sorted(dict.items(),
									key = lambda x:x[-1]['target_num'],
									reverse = True))

	# Find potential bridge GRPs with specific gene to link 2 regulons
	def __find_bridges_by_gene(self,
								gene,
								from_regulon,
								meta_grn,
								allowrance,
								grp_skip_list,
								combine_list,
								prev_grps):
		# last round to attempt find a bridge
		if allowrance == 0:
			for anchor, record in self.regulatory_sources.items():
				if record['regulon_id'] == from_regulon: continue
				# presume GRP which could link regulons
				grp_id = tool.Cast_GRP_ID(gene, anchor)
				if grp_id not in grp_skip_list and grp_id in meta_grn['grps']:
					anchor_reg_id = record['regulon_id']
					prev_grps.append(grp_id)
					# add grp to grp_skip_list
					for id in prev_grps: grp_skip_list[id] = None
					self.__update_combine_list(reg_id1 = from_regulon,
												reg_id2 = anchor_reg_id,
												grp_ids = prev_grps,
												combine_list = combine_list)

		elif allowrance > 0:
			for grp_id, grp in meta_grn['grps'].items():
				if grp_id in grp_skip_list: continue
				if grp['regulatory_source'] == gene:
					new = grp['regulatory_target']
				elif grp['regulatory_target'] == gene:
					new = grp['regulatory_source']
				else: continue
				if (new in self.regulatory_sources and
					self.regulatory_sources[new]['regulon_id'] != from_regulon):
					anchor_reg_id = self.regulatory_sources[new]['regulon_id']
					prev_grps.append(grp_id)
					# add grp to grp_skip_list
					for id in prev_grps: grp_skip_list[id] = None
					self.__update_combine_list(reg_id1 = from_regulon,
												reg_id2 = anchor_reg_id,
												grp_ids = prev_grps,
												combine_list = combine_list)
				else:
					prev_grps.append(grp_id)
					self.__find_bridges_by_gene(new,
												from_regulon,
												meta_grn,
												allowrance - 1,
												grp_skip_list,
												combine_list,
												prev_grps)

		else:
			raise lib.Error('Reached a negative allowrance value')

	# update combine_list if a GRP found can be the bridge between regulons
	def __update_combine_list(self, reg_id1, reg_id2, grp_ids, combine_list):
		# check action to perform
		ind_1 = None
		ind_2 = None
		for index, ele in enumerate(combine_list):
			# check which regulon set to add
			if reg_id1 in ele[0]: ind_1 = index
			if reg_id2 in ele[0]: ind_2 = index
		if ind_1 is None and ind_2 is None:
			combine_list.append([[reg_id1, reg_id2], [id for id in grp_ids]])
		# one of regulons already need to combine
		elif ind_1 is None and ind_2 is not None:
			combine_list[ind_2][0].append(reg_id1)
			combine_list[ind_2][1] += grp_ids
		elif ind_1 is not None and ind_2 is None:
			combine_list[ind_1][0].append(reg_id2)
			combine_list[ind_1][1] += grp_ids
		# both regulons already in combine list
		elif ind_1 == ind_2:
			combine_list[ind_1][1] += grp_ids
		else:
			combine_list[ind_1][1] += grp_ids
			combine_list[ind_1][0] += combine_list[ind_2][0]
			combine_list[ind_1][1] += combine_list[ind_2][1]
			del combine_list[ind_2]

	def __update_regulon_gene_list(self, source, target, gene_list, reversable):
		assert source not in gene_list[target]['source']
		assert source not in gene_list[target]['target']
		assert target not in gene_list[source]['source']
		assert target not in gene_list[source]['target']
		gene_list[target]['source'].append(source)
		gene_list[source]['target'].append(target)
		if reversable:
			gene_list[source]['source'].append(target)
			gene_list[target]['target'].append(source)

	def __update_regulon_with_grp(self, grp):
		update_ind = None
		combine_ind = None
		source_regulon_ind = None
		target_regulon_ind = None
		source = grp['regulatory_source']
		target = grp['regulatory_target']

		# check whether GRP could be appended into an exist regulon
		for i, regulon in enumerate(self.regulons):
			if source in regulon['genes']:
				assert source_regulon_ind is None
				source_regulon_ind = i
			if target in regulon['genes']:
				assert target_regulon_ind is None
				target_regulon_ind = i

		if source_regulon_ind is None and target_regulon_ind is None:
			# make new regulon data
			regulon = {
				'grps':{grp['id']: grp},
				'genes':{	source: {'source':[], 'target':[], 'type':TYPES[2]},
							target: {'source':[], 'target':[], 'type':TYPES[2]}
						}
			}
			self.regulons.append(regulon)
			return
		elif source_regulon_ind is not None and target_regulon_ind is not None:
			if source_regulon_ind == target_regulon_ind:
				update_ind = source_regulon_ind
			# combine regulons if two are involved
			elif source_regulon_ind != target_regulon_ind:
				update_ind = source_regulon_ind
				combine_ind = target_regulon_ind
		elif source_regulon_ind is not None:
			update_ind = source_regulon_ind
		elif target_regulon_ind is not None:
			update_ind = target_regulon_ind
		else:
			raise lib.Error('Something wrong with regulon updating process')

		# update regulon if found destination
		if update_ind is not None:
			# append GRP into self.regulons[update_ind]
			assert grp['id'] not in self.regulons[update_ind]['grps']
			self.regulons[update_ind]['grps'][grp['id']] = grp
			# update gene list
			if source not in self.regulons[update_ind]['genes']:
				self.regulons[update_ind]['genes'][source] = {	'source':[],
																'target':[],
																'type':TYPES[2]}
			elif target not in self.regulons[update_ind]['genes']:
				self.regulons[update_ind]['genes'][target] = {	'source':[],
																'target':[],
																'type':TYPES[2]}

		# combine 2 regulons if new GRP can connect two
		if combine_ind is not None:
			self.__combine_regulons(ind_1 = update_ind, ind_2 = combine_ind)
			del self.regulons[combine_ind]
