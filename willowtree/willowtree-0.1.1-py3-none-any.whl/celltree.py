from tree import Node, Tree
import copy

class cellNode(Node):
    def __init__(self, name='', edge_len = 0, parent = None):
        super().__init__(self, name='', edge_len = 0, parent = None)
        self.CNVs = []
        self.whole_chrom_events = []
        self.genome = None

    def inheret(self):
        self.genome = copy.deepcopy(self.parent.genome)

class cellTree(Tree):
    def __init__(self, root=None, newick=None):
        super().__init__(self, root=None, newick=None)

    def get_mutations(self):
        mutations = []
        for node in self.iter_descendants():
            mutations += node.whole_chrom_events
            mutations += node.CNVs
        return mutations