#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import make_unaligned_seqs, make_aligned_seqs


# In[2]:


seqs = {
    "hum": "AAGCAGATCCAGGAAAGCAGCGAGAATGGCAGCCTGGCCGCGCGCCAGGAGAGGCAGGCCCAGGTCAACCTCACT",
    "mus": "AAGCAGATCCAGGAGAGCGGCGAGAGCGGCAGCCTGGCCGCGCGGCAGGAGAGGCAGGCCCAAGTCAACCTCACG",
    "rat": "CTGAACAAGCAGCCACTTTCAAACAAGAAA",
}
unaligned_DNA = make_unaligned_seqs(seqs, moltype="dna")
print(unaligned_DNA.to_fasta())


# In[3]:


unaligned_aa = unaligned_DNA.get_translation()
print(unaligned_aa.to_fasta())


# In[4]:


aligned_aa_seqs = {
    "hum": "KQIQESSENGSLAARQERQAQVNLT",
    "mus": "KQIQESGESGSLAARQERQAQVNLT",
    "rat": "LNKQ------PLS---------NKK",
}
aligned_aa = make_aligned_seqs(aligned_aa_seqs, moltype="protein")
aligned_DNA = aligned_aa.replace_seqs(unaligned_DNA)
aligned_DNA

