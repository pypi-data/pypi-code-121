#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import DNA

my_seq = DNA.make_seq("AGTACACTGGT")
my_seq
print(my_seq)
str(my_seq)


# In[2]:


from cogent3 import RNA

rnaseq = RNA.make_seq("ACGUACGUACGUACGU")


# In[3]:


from cogent3 import DNA

my_seq = DNA.make_seq("AGTACACTGGT")
print(my_seq.to_fasta())


# In[4]:


from cogent3 import RNA

rnaseq = RNA.make_seq("ACGUACGUACGUACGU")
rnaseq.to_fasta()


# In[5]:


from cogent3 import make_seq

my_seq = make_seq("AGTACACTGGT", "my_gene", moltype="dna")
my_seq
type(my_seq)


# In[6]:


from cogent3 import make_seq

my_seq = make_seq("AGTACACTGGT", moltype="dna")
my_seq.name = "my_gene"
print(my_seq.to_fasta())


# In[7]:


from cogent3 import DNA

my_seq = DNA.make_seq("AGTACACTGGT")
print(my_seq.complement())


# In[8]:


print(my_seq.rc())


# In[9]:


print(my_seq.rc())


# In[10]:


from cogent3 import DNA

my_seq = DNA.make_seq("GCTTGGGAAAGTCAAATGGAA", "protein-X")
pep = my_seq.get_translation()
type(pep)
print(pep.to_fasta())


# In[11]:


from cogent3 import DNA

my_seq = DNA.make_seq("ACGTACGTACGTACGT")
print(my_seq.to_rna())


# In[12]:


from cogent3 import RNA

rnaseq = RNA.make_seq("ACGUACGUACGUACGU")
print(rnaseq.to_dna())


# In[13]:


from cogent3 import DNA

a = DNA.make_seq("AGTACACTGGT")
a.can_pair(a.complement())
a.can_pair(a.rc())


# In[14]:


from cogent3 import DNA

my_seq = DNA.make_seq("AGTACACTGGT")
extra_seq = DNA.make_seq("CTGAC")
long_seq = my_seq + extra_seq
long_seq
str(long_seq)


# In[15]:


my_seq[1:6]


# In[16]:


from cogent3 import DNA

seq = DNA.make_array_seq("ATGATGATGATG")
pos3 = seq[2::3]
assert str(pos3) == "GGGG"


# In[17]:


from cogent3 import DNA

seq = DNA.make_seq("ATGATGATGATG")
indices = [(i, i + 2) for i in range(len(seq))[::3]]
pos12 = seq.add_feature("pos12", "pos12", indices)
pos12 = pos12.get_slice()
assert str(pos12) == "ATATATAT"


# In[18]:


from cogent3 import RNA

s = RNA.make_seq("--AUUAUGCUAU-UAu--")
print(s.degap())

