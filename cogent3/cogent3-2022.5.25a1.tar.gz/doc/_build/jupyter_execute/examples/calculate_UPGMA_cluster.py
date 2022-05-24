#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs
from cogent3.evolve import distance
from cogent3.cluster.UPGMA import upgma


# In[3]:


from cogent3.evolve.models import HKY85


# In[4]:


al = load_aligned_seqs("data/test.paml")


# In[5]:


d = distance.EstimateDistances(al, submodel=HKY85())
d.run(show_progress=False)


# In[6]:


mycluster = upgma(d.get_pairwise_distances())
print(mycluster.ascii_art())


# In[7]:


mycluster.write("test_upgma.tree")


# In[8]:


import os

os.remove("test_upgma.tree")

