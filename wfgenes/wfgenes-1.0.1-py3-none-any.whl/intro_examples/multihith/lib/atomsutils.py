""" classes and functions for working with atoms using ASE """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

import numpy as np
from igraph import Graph
from ase.neighborlist import NeighborList
from ase.neighborlist import neighbor_list

def collinear(atom1, atom2, atom3):
    """ test collinearity of three atoms """
    vec1 = atom1.position - atom2.position
    vec2 = atom1.position - atom3.position
    tol = np.sqrt(np.finfo(np.float).eps)
    return np.linalg.norm(np.cross(vec1, vec2)) < tol


def make_graph_dict(atoms, cutoff=1.4, method='n1'):
    """ linearly (n1) and quadratically (n2) scaling algorithm """
    if method == 'n1':
        cutoff = 2.1*cutoff
        els = {tuple(sorted(t)) for t in zip(*neighbor_list('ij', atoms, cutoff))}
    if method == 'n2':
        nl = NeighborList(cutoffs=len(atoms)*[cutoff], bothways=False,
                          self_interaction=False)
        nl.update(atoms)
        els = [(a.index, n) for a in atoms for n in nl.get_neighbors(a.index)[0]]
    return {'n': len(atoms), 'edges': list(els), 'vertex_attrs': {'id': list(range(len(atoms)))}}


def make_graph(atoms, cutoff=1.4, method='n1'):
    """ alternative to AtomsGraph class for faster pickle/unpickle """
    return Graph(**make_graph_dict(atoms, cutoff, method))


class AtomsGraph(Graph):
    """ construct a graph for a structure in an Atoms object """
    def __init__(self, atoms, cutoff=1.4, method='n1'):
        self.args = (atoms, cutoff, method)
        graph_dict = make_graph_dict(atoms, cutoff, method)
        super(AtomsGraph, self).__init__(**graph_dict)

    def __reduce__(self):
        info = super(AtomsGraph, self).__reduce__()
        return (info[0], self.args)
