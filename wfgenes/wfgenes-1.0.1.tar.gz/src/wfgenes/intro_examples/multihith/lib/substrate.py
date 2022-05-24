""" generic classes and functions to model substrate-adsorbate systems """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

from ase import Atoms
from structure import Structure


class Substrate(Structure):
    """ generic substrate class """

    def get_gcn(self, sidxs):
        """ calculate the generalized coordination number, fcc only """
        cnmax = {1: 12, 2: 18, 3: 22, 4: 26}
        assert len(self.graph.subgraph(sidxs).clusters()) == 1
        nei = {n for idx in sidxs for n in self.graph.neighbors(idx) if n not in sidxs}
        cns = [self.graph.degree(idx) for idx in nei]
        return sum(cns)/cnmax[len(sidxs)]

    def get_cn(self, sidxs):
        """ calculate the coordination number """
        assert len(self.graph.subgraph(sidxs).clusters()) == 1
        nei = {n for idx in sidxs for n in self.graph.neighbors(idx) if n not in sidxs}
        return len(nei)


class SubstrateAdsorbateComplex(Structure):
    """ substrate-adsorbate complex superclass with generic methods """
    def __init__(self, substr, **kwargs):
        self.substr = substr.copy()
        self.adsorb = Atoms()
        atoms = self.substr.atoms + self.adsorb
        super(SubstrateAdsorbateComplex, self).__init__(atoms, **kwargs)
