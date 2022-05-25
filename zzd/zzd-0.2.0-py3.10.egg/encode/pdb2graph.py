import numpy as np
from numpy import linalg as LA
from Bio.PDB import *
import scipy.sparse as sp

"""

"""

def get_seq_and_coord(pdb_file=None, pdb_id="", pdb_chain="A"):
    """
    pdb_file:file of pdb 
    output seq and coordinate  of a pdb file.
    """
    amino2abv = {
            'ALA':'A',    'ARG':'R',  'ASN':'N',  'ASP':'D',  'CYS':'C',
            'GLN':'Q',    'GLU':'E',  'GLY':'G',  'HIS':'H',  'ILE':'I',
            'LEU':'L',    'LYS':'K',  'MET':'M',  'PHE':'F',  'PRO':'P',
            'SER':'S',    'THR':'T',  'TRP':'W',  'TYR':'Y',  'VAL':'V'}

    structure = PDBParser().get_structure(pdb_id,pdb_file)
    chain = [j for i in list(structure[0]) if i.id == pdb_chain for j in list(i)]
    seq = ''.join([amino2abv[i.resname] for i in chain])
    coord = np.array([np.mean([j.coord for j in i],axis=0) for i in chain])
    return seq, coord


def get_feature(seq):
    """ onehot encode feature """
    aminos = {i:idx for idx,i in enumerate('ARNDCQEGHILKMFPSTWYV')}
    arr = np.array([aminos[i] for i in seq])
    v =  np.eye(20)[arr]
    return sp.csr_matrix(v)


def get_adj(coord, threshold=9.5, max_length=None):
    """  normal adjacency of protein """
    distance_matrix =  LA.norm(np.array([i-coord  for i in coord]),axis=2)
    adj = np.array(distance_matrix < threshold,float)
    adj = sp.csr_matrix(adj) 
    adj = normalize(adj)
    return adj

def get_rdist(coord, threshold=9.5, max_length=None):
    """  normal adjacency of protein """
    distance_matrix =  LA.norm(np.array([i-coord  for i in coord]),axis=2)
    d = distance_matrix + sp.eye(distance_matrix.shape[0])
    rd = np.power(d,-1)
    rd[np.isinf(d)] = 0
    rd = rd * np.array(rd>0.09,float)
    rd = sp.csr_matrix(rd) 
    return rd

def get_graph(pdb_file=None,mode='rd'):
    """
    """
    seq, coord = get_seq_and_coord(pdb_file)
    feature = get_feature(seq)
    if mode=='rd':
        adj = get_rdist(coord)
    else:
        adj = get_adj(coord)
    return feature,adj


def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx


if __name__ == "__main__":
    pdb_file = "../lib/pdb/AF-A0A0A7EPL0-F1-model_v2.pdb"
    seq, coord = get_seq_and_coord(pdb_file)
    
    adj, feature = get_graph("../lib/pdb/AF-A0A0A7EPL0-F1-model_v2.pdb")
    print("adj:\n",adj)
    print("feature:\n",feature)
    print(f"shape",adj.shape, feature.shape)

















#more info
    #'ASX':'B' represent Asp or Asn
    #'GLX':'Z' represent Glu or Gln
    #'XLE':'J' represent 
    #'XAA':'X' represent random
    #'PYL':'O' represent Pyrrolysine encoded by the 'amber' stop codon UAG)is an α-amino acid that is used in the biosynthesis of
    #proteins in some methanogenic archaea and bacteria;it is not present in humans
    #'SEC':'U' Selenocysteine (symbol Sec or U,[2] in older publications also as Se-Cys)[3] is the 21st proteinogenic amino acid


