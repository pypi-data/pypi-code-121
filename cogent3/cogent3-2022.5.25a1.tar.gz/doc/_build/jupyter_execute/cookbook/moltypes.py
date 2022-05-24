#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import available_moltypes

available_moltypes()


# In[3]:


from cogent3 import load_aligned_seqs

seqs = load_aligned_seqs("data/brca1-bats.fasta", moltype="dna")


# In[4]:


from cogent3 import get_moltype

dna = get_moltype("dna")
dna


# In[5]:


dna.ambiguities


# In[6]:


dna.degenerates


# In[7]:


dna.complement("AGG")


# In[8]:


seq = dna.make_seq("AGGCTT", name="seq1")
seq


# In[9]:


rna = get_moltype("rna")
rna.is_valid("ACGUACGUACGUACGU")


# In[10]:


from cogent3.core import moltype as mt

DNAgapped = mt.MolType(
    seq_constructor=mt.DnaSequence,
    motifset=mt.IUPAC_DNA_chars,
    ambiguities=mt.IUPAC_DNA_ambiguities,
    complements=mt.IUPAC_DNA_ambiguities_complements,
    pairs=mt.DnaStandardPairs,
    gaps=".",
)
seq = DNAgapped.make_seq("ACG.")
seq


# In[11]:


from cogent3 import DNA
from cogent3.core.sequence import DnaSequence

DnaSequence.moltype = DNA

