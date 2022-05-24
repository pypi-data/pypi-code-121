#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io, translate

reader = io.load_unaligned(format="fasta")
to_aa = translate.translate_seqs()
process = reader + to_aa
seqs = process("data/SCA1-cds.fasta")


# In[3]:


from cogent3.app.align import progressive_align

aa_aligner = progressive_align("protein")
aligned = aa_aligner(seqs)
aligned


# In[4]:


aa_aligner = progressive_align("protein", distance="paralinear")
aligned = aa_aligner(seqs)
aligned


# In[5]:


aligned.info

