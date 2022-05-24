#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
tree = aln.quick_tree(calc="TN93", show_progress=False)
tree = tree.balanced()  # purely for display
print(tree.ascii_art())


# In[3]:


tree = aln.quick_tree(calc="TN93", bootstrap=100, show_progress=False)


# In[4]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
dists = aln.distance_matrix(calc="TN93")
tree = dists.quick_tree(show_progress=False)
tree = tree.balanced()  # purely for display
print(tree.ascii_art())


# In[5]:


from cogent3.phylo import nj
from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
dists = aln.distance_matrix(calc="TN93")
tree = nj.nj(dists, show_progress=False)
tree = tree.balanced()  # purely for display
print(tree.ascii_art())


# In[6]:


from cogent3.phylo import nj

dists = {("a", "b"): 2.7, ("c", "b"): 2.33, ("c", "a"): 0.73}
tree = nj.nj(dists, show_progress=False)
print(tree.ascii_art())


# In[7]:


from cogent3.util.deserialise import deserialise_object
from cogent3.phylo.least_squares import WLS

dists = deserialise_object("data/dists_for_phylo.json")
ls = WLS(dists)
stat, tree = ls.trex(a=5, k=5, show_progress=False)


# In[8]:


from cogent3 import load_aligned_seqs
from cogent3.phylo.maximum_likelihood import ML
from cogent3.evolve.models import F81

aln = load_aligned_seqs("data/primate_brca1.fasta")
ml = ML(F81(), aln)

