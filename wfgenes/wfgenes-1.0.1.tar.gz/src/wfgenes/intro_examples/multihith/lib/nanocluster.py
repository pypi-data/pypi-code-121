""" building and manipulating metal nanocluster models """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

from substrate import Substrate
from ase.constraints import FixAtoms

class Nanocluster(Substrate):
    """ construct and manipulate metallic nanoclusters """
    def __init__(self, params):
        super(Nanocluster, self).__init__(**params)

    def set_tags(self):
        graph = self.graph.copy()
        graph.vs['id'] = range(len(graph.vs))
        layer = 1
        tags = len(self.atoms)*[0]
        while len(graph.vs) > 0:
            ids = [s['id'] for s in graph.vs if graph.degree(s.index) != 12]
            ind = [s.index for s in graph.vs if graph.degree(s.index) != 12]
            for id_ in ids:
                tags[id_] = layer
            graph.delete_vertices(ind)
            layer += 1
        self.atoms.set_tags(tags)

    def set_constraints(self, constraints):
        if constraints is None:
            return
        if all('layers' not in c for c in constraints):
            super(Nanocluster, self).set_constraints(constraints)
            return
        for constraint in constraints:
            fixed = [i for i, tag in enumerate(self.atoms.get_tags())
                     if tag in constraint['layers']]
            self.atoms.set_constraint(FixAtoms(indices=fixed))
