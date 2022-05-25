import numpy as np
from numpy import linalg as LA
from Bio.PDB import *
import gzip
"""

"""
def fetch_pdb_coord(pdb_file=None, pdb_id="", pdb_chain="A"):
    """
    input:
        pdb_file:file of pdb 
    output
         seq and coordinate  of a pdb file.
    """
    amino2abv = {'ALA':'A',    'ARG':'R',  'ASN':'N',  'ASP':'D', 'CYS':'C',
              'GLN':'Q',    'GLU':'E',  'GLY':'G',  'HIS':'H',  'ILE':'I',
              'LEU':'L',    'LYS':'K',  'MET':'M',  'PHE':'F',  'PRO':'P',
              'SER':'S',    'THR':'T',  'TRP':'W',  'TYR':'Y',  'VAL':'V'}
    #'ASX':'B' represent Asp or Asn
    #'GLX':'Z' represent Glu or Gln
    #'XLE':'J' represent 
    #'XAA':'X' represent random
    #'PYL':'O' represent Pyrrolysine encoded by the 'amber' stop codon UAG) is an α-amino acid that is used in the biosynthesis of proteins in some methanogenic archaea and bacteria;it is not present in humans
    #'SEC':'U' Selenocysteine (symbol Sec or U,[2] in older publications also as Se-Cys)[3] is the 21st proteinogenic amino acid
    if pdb_file[-2:] == 'gz':
        with gzip.open(pdb_file,'rt') as f:
            structure = PDBParser().get_structure(pdb_id,f)
    else:
        structure = PDBParser().get_structure(pdb_id,pdb_file)

    chain = [j for i in list(structure[0]) if i.id == pdb_chain for j in list(i)]
    seq = ''.join([amino2abv[i.resname] for i in chain])
    coord = np.array([np.mean([j.coord for j in i],axis=0) for i in chain])
    return seq, coord


def pdb_adjacency(coord, threshold=9.5, max_length=None):
    """
    fetch normal adjacency of protein
    chain_amino_coord => distance_matrix => adjacency_matrix => normal_adjacency_matrix
    """
    distance_matrix =  LA.norm(np.array([i-coord  for i in coord]),axis=2)
    adjacency_matrix = np.array(distance_matrix < threshold, dtype=int)
    return adjacency_matrix


def pdb2dpc(pdb_file=None):
    """
    """
    aminos = 'ARNDCQEGHILKMFPSTWYV'
    dpc = { k:0 for k in [i+j for i in aminos for j in aminos]}

    seq , coord = fetch_pdb_coord(pdb_file)
    adjacency = pdb_adjacency(coord)

    for row in range(len(seq)):
        for col in range(len(seq)):
            if adjacency[row,col] == 1:
                k=seq[row]+seq[col]
                dpc[k]+=1

    value = np.array(list(dpc.values())) / (len(seq)-1)
    return value

if __name__ == "__main__":
    test = pdb2dpc("../lib/pdb/AF-A0A0A7EPL0-F1-model_v2.pdb.gz")
    print(test,test.shape)

