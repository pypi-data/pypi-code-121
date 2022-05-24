#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import get_code

standard_code = get_code(1)
standard_code.translate("TTTGCAAAC")


# In[2]:


from cogent3 import make_seq, get_code

standard_code = get_code(1)
seq = make_seq("ATGCTAACATAAA", moltype="dna")
translations = standard_code.sixframes(seq)
print(translations)


# In[3]:


from cogent3 import make_seq, get_code

standard_code = get_code(1)
seq = make_seq("ATGCTAACATAAA", moltype="dna")
stops_frame1 = standard_code.get_stop_indices(seq, start=0)
stops_frame1
stop_index = stops_frame1[0]
seq[stop_index : stop_index + 3]


# In[4]:


from cogent3 import make_seq, get_code

standard_code = get_code(1)
standard_code["TTT"]


# In[5]:


standard_code["A"]


# In[6]:


from cogent3 import get_code

standard_code = get_code(1)
standard_code["TTT"]


# In[7]:


from cogent3 import get_code

standard_code = get_code(1)
standard_code["A"]


# In[8]:


targets = ["A", "C"]
codons = [standard_code[aa] for aa in targets]
codons
flat_list = sum(codons, [])
flat_list


# In[9]:


from cogent3 import make_seq

my_seq = make_seq("AGTACACTGGTT", moltype="dna")
sorted(my_seq.codon_alphabet())
len(my_seq.codon_alphabet())


# In[10]:


from cogent3 import make_seq

my_seq = make_seq("ATGCACTGGTAA", name="my_gene", moltype="dna")
codons = my_seq.get_in_motif_size(3)
print(codons)


# In[11]:


pep = my_seq.get_translation()


# In[12]:


from cogent3 import make_seq

my_seq = make_seq("ATGCACTGGTAA", name="my_gene", moltype="dna")
seq = my_seq.trim_stop_codon()
pep = seq.get_translation()
print(pep.to_fasta())
print(type(pep))


# In[13]:


from cogent3 import make_seq

my_seq = make_seq("CAAATGTATTAA", name="my_gene", moltype="dna")
pep = my_seq[:-3].get_translation()
print(pep.to_fasta())

