#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import available_models

available_models("codon")


# In[3]:


from cogent3.app import io, evo

loader = io.load_aligned(format="fasta", moltype="dna")
aln = loader("data/primate_brca1.fasta")
model = evo.model(
    "CNFGTR",
    tree="data/primate_brca1.tree",
    sm_args=dict(optimise_motif_probs=True),
)
result = model(aln)
result


# In[4]:


result.lf

