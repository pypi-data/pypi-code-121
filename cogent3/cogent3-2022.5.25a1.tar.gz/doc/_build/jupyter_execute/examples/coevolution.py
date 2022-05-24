#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import make_aligned_seqs
from cogent3.core.alignment import ArrayAlignment
from cogent3.evolve.coevolution import validate_alignment

aln = make_aligned_seqs(
    {"1": "GAA", "2": "CTA", "3": "CTC", "4": "-TC"},
    moltype="protein",
    array_align=True,
)
validate_alignment(aln)


# In[2]:


from cogent3 import make_aligned_seqs
from cogent3.core.alignment import ArrayAlignment

aln = make_aligned_seqs(
    {"1": "AAA", "2": "CTA", "3": "CTC", "4": "-TC"},
    moltype="protein",
    array_align=True,
)


# In[3]:


from cogent3.evolve.coevolution import coevolve_pair_functions, coevolve_pair

coevolve_pair(coevolve_pair_functions["mi"], aln, pos1=1, pos2=2)


# In[4]:


from cogent3.evolve.coevolution import coevolve_pair_functions, coevolve_pair

coevolve_pair(coevolve_pair_functions["sca"], aln, pos1=1, pos2=2, cutoff=0.5)


# In[5]:


from cogent3.evolve.coevolution import (
    coevolve_position_functions,
    coevolve_position,
)

coevolve_position(coevolve_position_functions["mi"], aln, position=1)


# In[6]:


from cogent3.evolve.coevolution import (
    coevolve_alignment_functions,
    coevolve_alignment,
)

coevolve_alignment(coevolve_alignment_functions["mi"], aln)


# In[7]:


print(coevolve_pair_functions.keys())


# In[8]:


from cogent3.evolve.coevolution import (
    coevolve_alignment_functions,
    coevolve_alignments,
)

aln1 = make_aligned_seqs(
    {
        "human+protein1": "AAA",
        "pig+protein1": "CTA",
        "chicken+protein1": "CTC",
        "echidna+weird_db_identifier": "-TC",
    },
    moltype="protein",
    array_align=True,
)
aln2 = make_aligned_seqs(
    {
        "pig+protein2": "AAAY",
        "chicken+protein2": "CTAY",
        "echidna+protein2": "CTCF",
        "human+protein2": "-TCF",
    },
    moltype="protein",
    array_align=True,
)
coevolve_alignments(coevolve_alignment_functions["mi"], aln1, aln2)

