#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, load_tree
from cogent3.evolve.models import MG94HKY

aln = load_aligned_seqs("data/long_testseqs.fasta")
tree = load_tree("data/test.tree")


# In[3]:


sm = MG94HKY()
lf = sm.make_likelihood_function(tree, digits=2, space=3)
lf.set_alignment(aln)


# In[4]:


print(tree.ascii_art())


# In[5]:


lf.set_param_rule(
    "omega",
    tip_names=["DogFaced", "Mouse"],
    outgroup_name="Human",
    init=2.0,
    clade=True,
)
lf


# In[6]:


lf.set_param_rule("omega", init=1.0)
lf.set_param_rule(
    "omega",
    tip_names=["Human", "HowlerMon"],
    outgroup_name="Mouse",
    init=2.0,
    stem=True,
    clade=False,
)
lf


# In[7]:


lf.set_param_rule("omega", init=1.0)


# In[8]:


lf.set_param_rule(
    "omega",
    tip_names=["Human", "HowlerMon"],
    outgroup_name="Mouse",
    init=2.0,
    stem=True,
    clade=True,
)
lf


# In[9]:


lf.set_param_rule("omega", init=1.0)


# In[10]:


lf.set_param_rule(
    "omega",
    tip_names=["Human", "HowlerMon"],
    outgroup_name="Mouse",
    clade=True,
    value=1.0,
    is_constant=True,
)
lf.optimise(local=True, show_progress=False)
lf


# In[11]:


lf.set_param_rule(
    "omega",
    tip_names=["Human", "HowlerMon"],
    outgroup_name="Mouse",
    clade=True,
    is_constant=False,
)
lf.optimise(local=True, show_progress=False)
lf


# In[12]:


lf.set_param_rule(
    "omega",
    tip_names=["Human", "HowlerMon"],
    outgroup_name="Mouse",
    clade=True,
    is_independent=True,
)
lf.optimise(local=True, show_progress=False)
lf


# In[13]:


lf.set_param_rule("omega", is_independent=True)
lf.optimise(local=True, show_progress=False)
lf

