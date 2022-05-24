from igraph import Graph
import numpy as np

def get_resistance_distance(self, normalized=False):
    weights=None
    if self.is_weighted():
        weights='weight'
    L = np.array(self.laplacian(weights=weights, normalized=normalized))
    L_plus = np.linalg.pinv(L)
    shape = L_plus.shape
    Omega = np.empty(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            Omega[i][j] = L_plus[i][i]+L_plus[j][j]-L_plus[i][j]-L_plus[j][i]
    return Omega


def get_admittance_distance(self, normalized=False):
    Omega = self.get_resistance_distance(normalized=normalized)
    shape = Omega.shape
    Lambda = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            if i != j: Lambda[i][j] = 1./Omega[i][j]
    return Lambda


def get_kirchhoff_index(self, mode='resistance', normalized=False):
    if mode is 'resistance':
        matrix = self.get_resistance_distance()
    elif mode is 'admittance':
        matrix = self.get_admittance_distance()
    else:
        raise ValueError('invalid mode: ' + mode)
    if normalized:
        shape = matrix.shape
        return np.sum(matrix, axis=(0,1))/(shape[0]*shape[1])
    else:
        return np.sum(matrix, axis=(0,1))/2.


def get_spectrum(self, mode='laplacian'):
    if mode is 'laplacian':
        return np.sort(
            np.linalg.eigvals(self.laplacian(normalized=True))
            )
    elif mode is 'adjacency':
        if self.is_weighted():
            attribute = 'weight'
        else:
            attribute = None
        return np.sort(
            np.linalg.eigvals(self.get_adjacency(attribute=attribute).data)
            )
    else:
        raise ValueError('invalid mode: ' + mode)

Graph.get_kirchhoff_index = get_kirchhoff_index
Graph.get_resistance_distance = get_resistance_distance
Graph.get_admittance_distance = get_admittance_distance
Graph.get_spectrum = get_spectrum

"""
# generic method tests
#gr = Graph.Full(3)
#gr = Graph.Star(8)
#gr = Graph.Ring(6)
# gr = Graph.Full_Bipartite(4, 4)
# gr = Graph.Famous('Tetrahedral')
gr = Graph.Famous('Octahedral')
# gr = Graph.Famous('Cubical')
# gr = Graph.Formula('A-->B-->C-->D-->A')

print gr.get_resistance_distance()
print gr.get_kirchhoff_index()
print gr.get_spectrum()
"""

""" http://stackoverflow.com/questions/31034730/graph-analysis-identify-loop-paths """
def cycle_basis(G, root=None):
    gnodes = set(n.index for n in G.vs())
    cycles = []
    while gnodes: # loop over connected components
        if root is None:
            root = gnodes.pop()
        stack = [root]
        pred = {root:root} 
        used = {root:set()}
        while stack: # walk the spanning tree finding cycles
            z = stack.pop() # use last-in so cycles easier to find
            zused = used[z]
            for nbr in G.neighbors(z, mode='ALL'):
                if nbr not in used: # new node 
                    pred[nbr] = z
                    stack.append(nbr)
                    used[nbr] = set([z])
                elif nbr is z: # self loops
                    cycles.append([z]) 
                elif nbr not in zused: # found a cycle
                    pn = used[nbr]
                    cycle = [nbr,z]
                    p = pred[z]
                    while p not in pn:
                        cycle.append(p)
                        p = pred[p]
                    cycle.append(p)
                    cycles.append(cycle)
                    used[nbr].add(z)
        gnodes -= set(pred)
        root = None
    return cycles

"""
g = Graph()
g.add_vertices(9)
g.add_edges(
    [
    (0,1), (1,2), (2,0), (2,3), (3,0), (1,4), (4,5), 
    (5,2), (0,5), (0,6), (6,7), (7,8), (8,5)
    ]
)
print('cycle_basis_ig: ', cycle_basis(g))
"""

