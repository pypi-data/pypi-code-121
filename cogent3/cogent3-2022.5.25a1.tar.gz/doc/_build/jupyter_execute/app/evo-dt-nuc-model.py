#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, evo

loader = io.load_aligned(format="fasta", moltype="dna")
aln = loader("data/primate_brca1.fasta")
model = evo.model("BH", tree="data/primate_brca1.tree")
result = model(aln)
result


# In[3]:


result.lf


# In[4]:


tree = result.tree
fig = tree.get_figure()
fig.scale_bar = "top right"
fig.show(width=500, height=500)


# In[5]:


tabulator = evo.tabulate_stats()
stats = tabulator(result)
stats


# In[6]:


stats["edge motif motif2 params"]

