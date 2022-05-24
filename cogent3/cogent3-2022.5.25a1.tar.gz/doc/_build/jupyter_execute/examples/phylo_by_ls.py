#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


import pickle
from cogent3 import load_aligned_seqs
from cogent3.evolve import distance
from cogent3.evolve.models import HKY85
from cogent3.evolve.fast_distance import DistanceMatrix

al = load_aligned_seqs("data/long_testseqs.fasta")
d = distance.EstimateDistances(al, submodel=HKY85())
d.run(show_progress=False)

with open("dists_for_phylo.pickle", "wb") as f:
    pickle.dump(d.get_pairwise_distances(), f)


# In[3]:


import pickle
from cogent3.phylo import least_squares


# In[4]:


with open("dists_for_phylo.pickle", "rb") as f:
    dists = pickle.load(f)


# In[5]:


ls = least_squares.WLS(dists)


# In[6]:


ls_distance_matrix = least_squares.WLS(DistanceMatrix(dists))
ls_pairwise_matrix = least_squares.WLS(dists.to_dict())


# In[7]:


score, tree = ls.trex(a=5, k=1, show_progress=False)
assert score < 1e-4


# In[8]:


trees = ls.trex(a=5, k=5, return_all=True, show_progress=False)


# In[9]:


print(len(trees))


# In[10]:


wls_stats = [tree[0] for tree in trees]


# In[11]:


t1 = trees[0][1].balanced()
t2 = trees[1][1].balanced()
print(t1.ascii_art())


# In[12]:


print(t2.ascii_art())


# In[13]:


from cogent3 import make_tree

query_tree = make_tree(
    "((Human:.2,DogFaced:.2):.3,(NineBande:.1, Mouse:.5):.2,HowlerMon:.1)"
)


# In[14]:


ls.evaluate_tree(query_tree)


# In[15]:


wls, t = ls.evaluate_topology(query_tree)
assert "%.4f" % wls == "0.0084"


# In[16]:


import os

os.remove("dists_for_phylo.pickle")

