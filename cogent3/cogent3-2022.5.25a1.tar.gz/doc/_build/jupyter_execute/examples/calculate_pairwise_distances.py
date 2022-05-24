#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs
from cogent3.evolve import distance


# In[3]:


from cogent3.evolve.models import HKY85


# In[4]:


al = load_aligned_seqs("data/long_testseqs.fasta")


# In[5]:


d = distance.EstimateDistances(al, submodel=HKY85())
d.run(show_progress=False)
d.get_pairwise_distances()


# In[6]:


d.write("dists_for_phylo.phylip", format="phylip")


# In[7]:


import pickle

with open("dists_for_phylo.pickle", "wb") as f:
    pickle.dump(d.get_pairwise_distances(), f)


# In[8]:


import os

for file_name in "dists_for_phylo.phylip", "dists_for_phylo.pickle":
    os.remove(file_name)

