#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, load_tree
from cogent3.evolve.models import get_model
from cogent3.maths import stats


# In[3]:


al = load_aligned_seqs("data/long_testseqs.fasta")
t = load_tree("data/test.tree")


# In[4]:


sm = get_model("MG94GTR")


# In[5]:


lf = sm.make_likelihood_function(t, digits=2, space=2)


# In[6]:


lf.set_alignment(al)


# In[7]:


lf.optimise(global_tolerance=1.0, show_progress=False)


# In[8]:


lf


# In[9]:


null_lnL = lf.get_log_likelihood()
null_nfp = lf.get_num_free_params()


# In[10]:


lf.set_param_rule("omega", is_independent=True)


# In[11]:


lf.optimise(local=True, show_progress=False)


# In[12]:


lf


# In[13]:


at = lf.get_annotated_tree()


# In[14]:


LR = 2 * (lf.get_log_likelihood() - null_lnL)
df = lf.get_num_free_params() - null_nfp
P = stats.chisqprob(LR, df)


# In[15]:


print(f"Likelihood ratio statistic = {LR}")
print(f"degrees-of-freedom = {df}")
print(f"probability = {P}")

