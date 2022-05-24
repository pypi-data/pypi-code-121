#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, load_tree
from cogent3.evolve import bootstrap
from cogent3.evolve.models import HKY85
from cogent3.maths import stats


# In[3]:


def create_alt_function():
    t = load_tree("data/test.tree")
    sm = HKY85()
    return sm.make_likelihood_function(t)


# In[4]:


def create_null_function():
    lf = create_alt_function()
    # set the local clock for humans & howler monkey
    lf.set_local_clock("Human", "HowlerMon")
    return lf


# In[5]:


aln = load_aligned_seqs("data/long_testseqs.fasta")


# In[6]:


estimateP = bootstrap.EstimateProbability(
    create_null_function(), create_alt_function(), aln
)


# In[7]:


estimateP.set_num_replicates(5)


# In[8]:


estimateP.run(show_progress=False)


# In[9]:


p = estimateP.get_estimated_prob()


# In[10]:


print("%.2f, %.2f" % estimateP.get_observed_lnL())

