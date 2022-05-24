#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import available_codes

available_codes()


# In[3]:


from cogent3 import load_aligned_seqs

nt_seqs = load_aligned_seqs("data/brca1-bats.fasta", moltype="dna")
nt_seqs[:21]


# In[4]:


aa_seqs = nt_seqs.get_translation(gc=1, incomplete_ok=True)
aa_seqs[:20]


# In[5]:


from cogent3 import get_code

gc = get_code(4)
gc

