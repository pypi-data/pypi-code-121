#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import PROTEIN

p = PROTEIN.make_seq("THISISAPRQTEIN", "myProtein")
type(p)
str(p)


# In[3]:


from cogent3.core.genetic_code import DEFAULT as standard_code

standard_code.translate("TTTGCAAAC")


# In[4]:


from cogent3 import load_aligned_seqs

seq = load_aligned_seqs("data/abglobin_aa.phylip", moltype="protein")

