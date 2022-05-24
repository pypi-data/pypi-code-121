#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, load_tree
from cogent3.evolve.models import get_model
from cogent3.maths import stats


# In[3]:


aln = load_aligned_seqs("data/long_testseqs.fasta")
t = load_tree(filename="data/test.tree")


# In[4]:


sm = get_model("HKY85")


# In[5]:


lf = sm.make_likelihood_function(t, digits=2, space=3)


# In[6]:


lf.set_local_clock("Human", "HowlerMon")


# In[7]:


lf.set_alignment(aln)


# In[8]:


lf.optimise(show_progress=False)


# In[9]:


lf.set_name("clock")
lf


# In[10]:


null_lnL = lf.get_log_likelihood()
null_nfp = lf.get_num_free_params()


# In[11]:


lf.set_param_rule("length", is_independent=True)


# In[12]:


lf.optimise(show_progress=False)


# In[13]:


lf.set_name("non clock")
lf


# In[14]:


LR = 2 * (lf.get_log_likelihood() - null_lnL)
df = lf.get_num_free_params() - null_nfp
P = stats.chisqprob(LR, df)


# In[15]:


print("Likelihood ratio statistic = ", LR)
print("degrees-of-freedom = ", df)
print("probability = ", P)

