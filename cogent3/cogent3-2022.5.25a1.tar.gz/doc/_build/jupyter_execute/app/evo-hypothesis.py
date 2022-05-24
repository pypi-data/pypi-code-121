#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, evo, sample

loader = io.load_aligned(format="fasta", moltype="dna")
aln = loader("data/primate_brca1.fasta")


# In[3]:


tree = "data/primate_brca1.tree"
sm_args = dict(optimise_motif_probs=True)

null = evo.model("GTR", tree=tree, sm_args=sm_args)
alt = evo.model("GN", tree=tree, sm_args=sm_args)
hyp = evo.hypothesis(null, alt)
result = hyp(aln)
type(result)


# In[4]:


result


# In[5]:


result.LR, result.df, result.pvalue


# In[6]:


result.null


# In[7]:


result.null.lf


# In[8]:


result.alt.lf

