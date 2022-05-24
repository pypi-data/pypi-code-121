#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3.app.composable import ALIGNED_TYPE, appify

@appify(ALIGNED_TYPE, ALIGNED_TYPE, data_types="Alignment")
def up_to(val, index=4):
    return val[:index]


# In[2]:


up_to


# In[3]:


first4 = up_to(index=4)
first4


# In[4]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=dict(a="GCAAGCGTTTAT", b="GCTTTTGTCAAT"), array_align=False, moltype="dna"
)
result = first4(aln)
result


# In[5]:


from cogent3.app.composable import (
    ALIGNED_TYPE,
    SEQUENCE_TYPE,
    SERIALISABLE_TYPE,
    appify,
)

@appify((ALIGNED_TYPE, SEQUENCE_TYPE), SERIALISABLE_TYPE)
def rename_seqs(aln):
    """upper case names"""
    return aln.rename_seqs(lambda x: x.upper())

renamer = rename_seqs()
result = renamer(aln)
result


# In[6]:


from cogent3.app.composable import (
    ALIGNED_TYPE,
    PAIRWISE_DISTANCE_TYPE,
    appify,
)

@appify(ALIGNED_TYPE, PAIRWISE_DISTANCE_TYPE)
def get_dists(aln, calc="hamming"):
    return aln.distance_matrix(calc=calc, show_progress=False)

percent_dist = get_dists(calc="percent")
result = percent_dist(aln)
result

