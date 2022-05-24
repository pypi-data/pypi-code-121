#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, sample

reader = io.load_aligned(format="fasta", moltype="dna")
select_seqs = sample.take_named_seqs("Human", "Rhesus", "Galago")
process = reader + select_seqs
aln = process("data/primate_brca1.fasta")
aln.names


# In[3]:


from cogent3.app import evo

gn = evo.model("GN")
gn


# In[4]:


fitted = gn(aln)
type(fitted)


# In[5]:


fitted


# In[6]:


fitted.lf


# In[7]:


fitted.lnL, fitted.nfp


# In[8]:


fitted.source


# In[9]:


fitted.tree, fitted.alignment


# In[10]:


fitted.total_length(length_as="paralinear")


# In[11]:


gn = evo.model("GN", split_codons=True)

fitted = gn(aln)
fitted


# In[12]:


fitted[3]

