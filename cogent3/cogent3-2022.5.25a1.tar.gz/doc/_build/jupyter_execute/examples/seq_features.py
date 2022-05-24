#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import DNA

s = DNA.make_seq("aagaagaagacccccaaaaaaaaaattttttttttaaaaaaaaaaaaa", name="Orig")
exon1 = s.add_feature("exon", "exon1", [(10, 15)])
exon2 = s.add_feature("exon", "exon2", [(30, 40)])


# In[2]:


from cogent3.core.annotation import Feature

s2 = DNA.make_seq("aagaagaagacccccaaaaaaaaaattttttttttaaaaaaaaaaaaa", name="Orig2")
exon3 = s2.add_annotation(Feature, "exon", "exon1", [(35, 40)])


# In[3]:


s[exon1]


# In[4]:


exons = s.get_annotations_matching("exon")
print(exons)


# In[5]:


print(s.get_region_covering_all(exons))
s.get_region_covering_all(exons).get_slice()


# In[6]:


print(s.get_region_covering_all(exons).get_shadow().get_slice())


# In[7]:


exon1[0:3].get_slice()

