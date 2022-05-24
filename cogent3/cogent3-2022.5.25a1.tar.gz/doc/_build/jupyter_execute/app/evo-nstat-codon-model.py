#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, evo

loader = io.load_aligned(format="fasta", moltype="dna")
aln = loader("data/primate_brca1.fasta")


# In[3]:


model = evo.model("GNC", tree="data/primate_brca1.tree")
result = model(aln)
result


# In[4]:


result.lf


# In[5]:


tree = result.tree
fig = tree.get_figure()
fig.scale_bar = "top right"
fig.show(width=500, height=500)

