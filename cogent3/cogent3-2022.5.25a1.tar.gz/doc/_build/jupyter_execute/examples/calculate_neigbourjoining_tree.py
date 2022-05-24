#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs
from cogent3.evolve import distance
from cogent3.phylo import nj


# In[3]:


from cogent3.evolve.models import get_model


# In[4]:


al = load_aligned_seqs("data/long_testseqs.fasta")


# In[5]:


d = distance.EstimateDistances(al, submodel=get_model("HKY85"))
d.run(show_progress=False)


# In[6]:


mytree = nj.nj(d.get_pairwise_distances(), show_progress=False)
print(mytree.ascii_art())


# In[7]:


mytree.write("test_nj.tree")


# In[8]:


import os

os.remove("test_nj.tree")

