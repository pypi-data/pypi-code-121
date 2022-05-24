#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import available_distances

available_distances()


# In[3]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
dists = aln.distance_matrix(calc="tn93", show_progress=False)
dists


# In[4]:


from cogent3 import load_aligned_seqs, get_distance_calculator

aln = load_aligned_seqs("data/primate_brca1.fasta")
dist_calc = get_distance_calculator("tn93", alignment=aln)
dist_calc


# In[5]:


dist_calc.run(show_progress=False)
dists = dist_calc.get_pairwise_distances()
dists


# In[6]:


dist_calc.stderr


# In[7]:


from cogent3 import load_aligned_seqs, get_model
from cogent3.evolve import distance

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
d = distance.EstimateDistances(aln, submodel=get_model("F81"))
d.run(show_progress=False)
dists = d.get_pairwise_distances()
dists

