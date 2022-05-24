#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import DNA, PROTEIN

print(DNA.alphabet)
print(PROTEIN.alphabet)


# In[2]:


PROTEIN.alphabet.moltype == PROTEIN


# In[3]:


dinuc_alphabet = DNA.alphabet.get_word_alphabet(2)
print(dinuc_alphabet)
trinuc_alphabet = DNA.alphabet.get_word_alphabet(3)
print(trinuc_alphabet)


# In[4]:


seq = "TAGT"
indices = DNA.alphabet.to_indices(seq)
indices


# In[5]:


seq = DNA.alphabet.from_indices([0, 2, 3, 0])
seq


# In[6]:


seq = DNA.alphabet.from_ordinals_to_seq([0, 2, 3, 0])
seq

