#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_unaligned_seqs, make_tree
from cogent3.align.progressive import TreeAlign


# In[3]:


seqs = load_unaligned_seqs("data/test2.fasta", moltype="dna")
aln, tree = TreeAlign("HKY85", seqs, show_progress=False)
aln


# In[4]:


tree = make_tree(
    "(((NineBande:0.013,Mouse:0.185):0.023,DogFaced:0.046):0.027,Human:0.034,HowlerMon:0.019)"
)
params = {"kappa": 4.0}
aln, tree = TreeAlign(
    "HKY85", seqs, tree=tree, param_vals=params, show_progress=False
)
aln


# In[5]:


from cogent3 import load_unaligned_seqs, make_tree
from cogent3.align.progressive import TreeAlign

seqs = load_unaligned_seqs("data/test2.fasta", moltype="dna")
tree = make_tree(
    "((NineBande:0.058,Mouse:0.595):0.079,DogFaced:0.142,(HowlerMon:0.062,Human:0.103):0.079)"
)
params = {"kappa": 4.0, "omega": 1.3}
aln, tree = TreeAlign(
    "MG94HKY", seqs, tree=tree, param_vals=params, show_progress=False
)
aln


# In[6]:


from cogent3 import make_unaligned_seqs
from cogent3.evolve.models import get_model
from cogent3.align.progressive import TreeAlign

seqs = [
    (
        "hum",
        "AAGCAGATCCAGGAAAGCAGCGAGAATGGCAGCCTGGCCGCGCGCCAGGAGAGGCAGGCCCAGGTCAACCTCACT",
    ),
    (
        "mus",
        "AAGCAGATCCAGGAGAGCGGCGAGAGCGGCAGCCTGGCCGCGCGGCAGGAGAGGCAGGCCCAAGTCAACCTCACG",
    ),
    ("rat", "CTGAACAAGCAGCCACTTTCAAACAAGAAA"),
]
unaligned_DNA = make_unaligned_seqs(seqs, moltype="dna")
print(unaligned_DNA)


# In[7]:


print(unaligned_DNA.get_translation())


# In[8]:


from cogent3 import make_aligned_seqs

aligned_aa_seqs = [
    ("hum", "KQIQESSENGSLAARQERQAQVNLT"),
    ("mus", "KQIQESGESGSLAARQERQAQVNLT"),
    ("rat", "LNKQ------PLS---------NKK"),
]
aligned_aa = make_aligned_seqs(aligned_aa_seqs, moltype="protein")


# In[9]:


aligned_DNA = aligned_aa.replace_seqs(unaligned_DNA, aa_to_codon=True)
aligned_DNA

