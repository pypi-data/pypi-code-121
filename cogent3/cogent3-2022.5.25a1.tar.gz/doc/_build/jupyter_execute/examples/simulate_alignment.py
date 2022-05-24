#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
from cogent3 import make_tree
from cogent3.evolve.models import get_model


# In[2]:


t = make_tree("(a:0.4,b:0.3,(c:0.15,d:0.2)edge.0:0.1);")


# In[3]:


sm = get_model("F81")
lf = sm.make_likelihood_function(t)
lf.set_constant_lengths()
lf.set_motif_probs(dict(A=0.1, C=0.2, G=0.3, T=0.4))
lf


# In[4]:


simulated = lf.simulate_alignment(sequence_length=1000)
simulated

