#!/usr/bin/env python3
"""
Ageas Reborn
Predict potential Gene Regulatory Pathways(GRPs) using GRNBoost-Like algo

author: jy, nkmtmsys
"""

import ageas.tool as tool
from xgboost import XGBRegressor
from collections import OrderedDict
import ageas.lib as lib



class Predict:
    """
    Predict regulation targets for source TFs
    Essentially, this is stimulating how GRNBoost2 works
    But thread can be automatically set by checking confirmed GRPs
    """
    def __init__(self, gem_data, sample_grps = None, thread = None):
        super(Predict, self).__init__()
        assert sample_grps is not None or thread is not None
        self.class1_gem = gem_data.class1
        self.class2_gem = gem_data.class2
        self.thread = 1 / len(gem_data.genes)
        if thread is not None and thread != 'auto':
            self.thread = float(thread)
        elif thread == 'auto':
            self.thread = self.__auto_set_thread(sample_grps)
        else:
            raise lib.Error('Predictor thread setting is wrong')

    # Expand meta GRN by applying GRNBoost2-like algo on source TFs without
    # documented targets
    def expand_meta_grn(self, meta_grn, genes, correlation_thread):
        for gene in genes:
            class1FeatImpts, class2FeatImpts = self._getFeatureImportences(gene)
            self.__update_grps_to_meta_grn(meta_grn,
                                            correlation_thread,
                                            gene,
                                            self.class1_gem.index,
                                            class1FeatImpts,)
            self.__update_grps_to_meta_grn(meta_grn,
                                            correlation_thread,
                                            gene,
                                            self.class2_gem.index,
                                            class2FeatImpts,)
        return meta_grn

    # decide whether update GRPs associated with given gene into GRN guidance
    def __update_grps_to_meta_grn(self,
                                    meta_grn,
                                    correlation_thread,
                                    gene,
                                    gene_list,
                                    feature_importances,):
        if feature_importances is None: return
        for i in range(len(gene_list)):
            tar = gene_list[i]
            if feature_importances[i] > self.thread:
                if tool.Cast_GRP_ID(gene, tar) not in meta_grn:
                    tool.Update_Meta_GRN(meta_grn,
                                        gene,
                                        tar,
                                        self.class1_gem,
                                        self.class2_gem,
                                        correlation_thread)
        return

    # Automatically set prediction thread by tuning with sample GRPs
    # Essentially this part is finding a regulatory source having most
    # regulatory targets, and then find a confirmed GRP with minimum
    # importance predicted by GBM based method
    def __auto_set_thread(self, sample_grps):
        regulatory_sources = {}
        for grp in sample_grps:
            source = sample_grps[grp]['regulatory_source']
            if source not in regulatory_sources:
                regulatory_sources[source] = [grp]
            else:
                regulatory_sources[source].append(grp)
        regulatory_sources = OrderedDict(sorted(regulatory_sources.items(),
                                                key = lambda x: x[1]))
        # Choose a key presenting in both classes
        i = 0
        for src in regulatory_sources:
            if src in self.class1_gem.index and src in self.class2_gem.index:
                break
            if i == len(regulatory_sources) - 1:
                return self.thread
            i += 1
        grps = regulatory_sources[src]
        class1FeatImpts, class2FeatImpts = self._getFeatureImportences(src,True)
        assert len(self.class1_gem.index) == len(class1FeatImpts)
        assert len(self.class2_gem.index) == len(class2FeatImpts)
        genes = tool.Get_GRP_Genes(grps)
        # assign feature importances to each gene in selected reg source's GRPs
        for i in range(len(self.class1_gem.index)):
            if self.class1_gem.index[i] in genes and class1FeatImpts[i] > 0:
                genes[self.class1_gem.index[i]] = class1FeatImpts[i]
        for i in range(len(self.class2_gem.index)):
            gene = self.class2_gem.index[i]
            if gene in genes and class2FeatImpts[i] > 0:
                if genes[gene] == 0:
                    genes[gene] = class2FeatImpts[i]
                else:
                    genes[gene] = (genes[gene] + class2FeatImpts[i]) / 2
        # take out genes with 0 importances and reorder the dict
        genes = {x:genes[x] for x in genes if genes[x] > 0}
        genes = OrderedDict(sorted(genes.items(), key = lambda x: x[1]))
        return min(genes[next(iter(genes))], self.thread)

    # Basically, this part mimicing what GRNBoost2 does
    def _getFeatureImportences(self, key, checked_in_gem = False):
        if checked_in_gem or key in self.class1_gem.index:
            c1_result = self.__gbm_feature_importances_calculat(self.class1_gem,
                                                                key)
        else: c1_result = None
        if checked_in_gem or key in self.class2_gem.index:
            c2_result = self.__gbm_feature_importances_calculat(self.class2_gem,
                                                                key)
        else: c2_result = None
        return c1_result, c2_result

    # as named
    def __gbm_feature_importances_calculat(self, gem, key, random_state = 0):
        gbm = XGBRegressor(random_state = random_state)
        gbm.fit(gem.transpose(), list(gem.loc[[key]].values[0]))
        return gbm.feature_importances_
