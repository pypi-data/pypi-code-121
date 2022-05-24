#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3 import DNA
from cogent3.core.annotation import Feature

s = DNA.make_seq("AAGAAGAAGACCCCCAAAAAAAAAATTTTTTTTTTAAAAAAAAAAAAA", name="Orig")
exon1 = s.add_annotation(Feature, "exon", "fred", [(10, 15)])
exon2 = s.add_annotation(Feature, "exon", "trev", [(30, 40)])


# In[2]:


s[exon1]
exon1.get_slice()


# In[3]:


exons = s.get_annotations_matching("exon")
print(exons)


# In[4]:


dont_exist = s.get_annotations_matching("dont_exist")
dont_exist
s[dont_exist]


# In[5]:


print(s.get_region_covering_all(exons))
print(s.get_region_covering_all(exons).get_shadow())


# In[6]:


s.get_region_covering_all(exons).get_slice()


# In[7]:


s[exon1, exon2]


# In[8]:


print(s.get_region_covering_all(exons + exons))
s[exon1, exon1, exon1, exon1, exon1]


# In[9]:


s[15:20, 5:16]


# In[10]:


exon1[0:3].get_slice()


# In[11]:


c = s[exon1[4:]] + s
print(len(c))
for feat in c.annotations:
    print(feat)


# In[12]:


print(c[exon1])


# In[13]:


len(s.annotations)
region = s.get_region_covering_all(exons)
len(s.annotations)
region.attach()
len(s.annotations)
region.detach()
len(s.annotations)


# In[14]:


plus = DNA.make_seq("AAGGGGAAAACCCCCAAAAAAAAAATTTTTTTTTTAAA", name="plus")
plus_cds = plus.add_annotation(Feature, "CDS", "gene", [(2, 6), (10, 15), (25, 35)])
print(plus_cds.get_slice())
minus = plus.rc()
minus_cds = minus.get_annotations_matching("CDS")[0]
print(minus_cds.get_slice())


# In[15]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
print(aln)
exon = aln.get_seq("x").add_annotation(Feature, "exon", "fred", [(3, 8)])
aln_exons = aln.get_annotations_from_seq("x", "exon")
aln_exons = aln.get_annotations_from_any_seq("exon")


# In[16]:


print(exon)
print(aln_exons[0])
print(aln_exons[0].get_slice())
aln_exons[0].attach()
len(aln.annotations)


# In[17]:


exons = aln.get_projected_annotations("y", "exon")
print(exons)
print(aln.get_seq("y")[exons[0].map.without_gaps()])


# In[18]:


aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "TTTT--CCCC"]], array_align=False
)
s = DNA.make_seq("AAAAAAAAA", name="x")
exon = s.add_annotation(Feature, "exon", "fred", [(3, 8)])
exon = aln.get_seq("x").copy_annotations(s)
aln_exons = list(aln.get_annotations_from_seq("x", "exon"))
print(aln_exons)


# In[19]:


exon = aln.get_seq("y").copy_annotations(s)
aln_exons = list(aln.get_annotations_from_seq("y", "exon"))
print(aln_exons)
print(aln[aln_exons])


# In[20]:


aln = make_aligned_seqs([["x", "-AAAA"], ["y", "TTTTT"]], array_align=False)
seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCC", "x")
exon = seq.add_feature("exon", "A", [(5, 8)])
aln.get_seq("x").copy_annotations(seq)
copied = list(aln.get_annotations_from_seq("x", "exon"))
copied
copied[0].get_slice()


# In[21]:


aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCC", "x")
match_exon = seq.add_feature("exon", "A", [(5, 8)])
aln.get_seq("y").copy_annotations(seq)
copied = list(aln.get_annotations_from_seq("y", "exon"))
copied


# In[22]:


aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
diff_len_seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCCCCCCCCCC", "x")
nonmatch = diff_len_seq.add_feature("repeat", "A", [(12, 14)])
aln.get_seq("y").copy_annotations(diff_len_seq)
copied = list(aln.get_annotations_from_seq("y", "repeat"))
copied


# In[23]:


aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "------TTTT"]], array_align=False
)
exon = aln.get_seq("x").add_feature("exon", "fred", [(3, 8)])
aln_exons = list(aln.get_annotations_from_seq("x", "exon"))
print(aln_exons)
print(aln_exons[0].get_slice())
aln = make_aligned_seqs(
    [["x", "-AAAAAAAAA"], ["y", "TTTT--T---"]], array_align=False
)
exon = aln.get_seq("x").add_feature("exon", "fred", [(3, 8)])
aln_exons = list(aln.get_annotations_from_seq("x", "exon"))
print(aln_exons[0].get_slice())


# In[24]:


aln = make_aligned_seqs(
    [["x", "C-CCCAAAAA"], ["y", "-T----TTTT"]], moltype="dna", array_align=False
)
print(aln)
exon = aln.get_seq("x").add_feature("exon", "ex1", [(0, 4)])
print(exon)
print(exon.get_slice())
aln_exons = list(aln.get_annotations_from_seq("x", "exon"))
print(aln_exons)
print(aln_exons[0].get_slice())


# In[25]:


print(aln_exons[0].as_one_span().get_slice())


# In[26]:


aln_rc = aln.rc()
rc_exons = list(aln_rc.get_annotations_from_any_seq("exon"))
print(aln_rc[rc_exons])  # not using as_one_span, so gap removed from x
print(aln_rc[rc_exons[0].as_one_span()])


# In[27]:


all_exons = aln.get_region_covering_all(aln_exons)
coords = all_exons.get_coordinates()
assert coords == [(0, 1), (2, 5)]


# In[28]:


aln = make_aligned_seqs(
    [["x", "C-CCCAAAAAGGGAA"], ["y", "-T----TTTTG-GTT"]], array_align=False
)
print(aln)
exon = aln.get_seq("x").add_feature("exon", "norwegian", [(0, 4)])
print(exon.get_slice())
repeat = aln.get_seq("x").add_feature("repeat", "blue", [(9, 12)])
print(repeat.get_slice())
repeat = aln.get_seq("y").add_feature("repeat", "frog", [(5, 7)])
print(repeat.get_slice())


# In[29]:


print(aln.get_seq("x").with_masked_annotations("exon", mask_char="?"))
print(aln.get_seq("x").with_masked_annotations("exon", mask_char="?", shadow=True))
print(aln.get_seq("x").with_masked_annotations(["exon", "repeat"], mask_char="?"))
print(
    aln.get_seq("x").with_masked_annotations(
        ["exon", "repeat"], mask_char="?", shadow=True
    )
)
print(aln.get_seq("y").with_masked_annotations("exon", mask_char="?"))
print(aln.get_seq("y").with_masked_annotations("repeat", mask_char="?"))
print(
    aln.get_seq("y").with_masked_annotations("repeat", mask_char="?", shadow=True)
)


# In[30]:


print(aln.with_masked_annotations("exon", mask_char="?"))
print(aln.with_masked_annotations("exon", mask_char="?", shadow=True))
print(aln.with_masked_annotations("repeat", mask_char="?"))
print(aln.with_masked_annotations("repeat", mask_char="?", shadow=True))
print(aln.with_masked_annotations(["repeat", "exon"], mask_char="?"))
print(aln.with_masked_annotations(["repeat", "exon"], shadow=True))


# In[31]:


data = [["human", "CGAAACGTTT"], ["mouse", "CTAAACGTCG"]]
as_series = make_aligned_seqs(data, array_align=False)
as_items = make_aligned_seqs(data, array_align=False)


# In[32]:


as_series.get_seq("human").add_feature("cpgsite", "cpg", [(0, 2), (5, 7)])
as_series.get_seq("mouse").add_feature("cpgsite", "cpg", [(5, 7), (8, 10)])


# In[33]:


as_items.get_seq("human").add_feature("cpgsite", "cpg", [(0, 2)])
as_items.get_seq("human").add_feature("cpgsite", "cpg", [(5, 7)])
as_items.get_seq("mouse").add_feature("cpgsite", "cpg", [(5, 7)])
as_items.get_seq("mouse").add_feature("cpgsite", "cpg", [(8, 10)])


# In[34]:


serial = as_series.with_masked_annotations(["cpgsite"])
print(serial)
itemwise = as_items.with_masked_annotations(["cpgsite"])
print(itemwise)


# In[35]:


print(plus.with_masked_annotations("CDS"))
print(minus.with_masked_annotations("CDS"))

