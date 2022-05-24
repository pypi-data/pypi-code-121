#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app import io

reader = io.load_unaligned(format="fasta")
seqs = reader("data/SCA1-cds.fasta")


# In[3]:


from cogent3.app.align import progressive_align

codon_aligner = progressive_align("codon")
aligned = codon_aligner(seqs)
aligned


# In[4]:


aligned.info


# In[5]:


nt_aligner = progressive_align("codon", distance="paralinear")
aligned = nt_aligner(seqs)
aligned


# In[6]:


tree = "((Chimp:0.001,Human:0.001):0.0076,Macaque:0.01,((Rat:0.01,Mouse:0.01):0.02,Mouse_Lemur:0.02):0.01)"
codon_aligner = progressive_align("codon", guide_tree=tree)
aligned = codon_aligner(seqs)
aligned


# In[7]:


codon_aligner = progressive_align(
    "codon", guide_tree=tree, indel_rate=0.001, indel_length=0.01
)
aligned = codon_aligner(seqs)
aligned


# In[8]:


codon_aligner = progressive_align(
    "CNFHKY", guide_tree=tree, param_vals=dict(omega=0.1, kappa=3)
)
aligned = codon_aligner(seqs)
aligned


# In[9]:


aligned.info

