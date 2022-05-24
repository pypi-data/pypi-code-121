#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, evo

reader = io.load_aligned(format="fasta")
aln = reader("data/primate_brca1.fasta")
gn = evo.model("GN", tree="data/primate_brca1.tree")
result = gn(aln)


# In[3]:


reconstuctor = evo.ancestral_states()
states_result = reconstuctor(result)
states_result


# In[4]:


states_result["edge.0"]


# In[5]:


result.tree.get_figure(contemporaneous=True).show(width=500, height=500)

