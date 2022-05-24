#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.parse.genbank import RichGenbankParser

parser = RichGenbankParser(open("data/ST_genome_part.gb"))
for accession, seq in parser:
    print(accession)


# In[3]:


cds = seq.get_annotations_matching("CDS")
print(cds)


# In[4]:


from cogent3.core.annotation import Feature

def add_annotation(seq, feature, spans):
    type_ = feature["type"]
    if type_ != "CDS":
        return
    name = feature.get("locus_tag", None)
    if name and not isinstance(name, str):
        name = " ".join(name)
    seq.add_annotation(Feature, type_, name, spans)

parser = RichGenbankParser(
    open("data/ST_genome_part.gb"), add_annotation=add_annotation
)
for accession, seq in parser:  # just reading one accession,sequence
    break
genes = seq.get_annotations_matching("CDS")
print(genes)


# In[5]:


from cogent3 import DNA
from cogent3.core.annotation import Feature

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
print(s1[10:15])  # this will be exon 1
print(s1[30:40])  # this will be exon 2
print(s1[45:48])  # this will be exon 3
s2 = DNA.make_seq("CGAAACGTTT", name="seq2")
s3 = DNA.make_seq("CGAAACGTTT", name="seq3")


# In[6]:


from cogent3 import DNA
from cogent3.core.annotation import Feature

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
exon1 = s1.add_annotation(Feature, "exon", "A", [(10, 15)])
exon2 = s1.add_annotation(Feature, "exon", "B", [(30, 40)])


# In[7]:


from cogent3 import DNA

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
exon3 = s1.add_feature("exon", "C", [(45, 48)])


# In[8]:


from cogent3 import DNA

s2 = DNA.make_seq("CGAAACGTTT", name="seq2")
cpgs_series = s2.add_feature("cpgsite", "cpg", [(0, 2), (5, 7)])
s3 = DNA.make_seq("CGAAACGTTT", name="seq3")
cpg1 = s3.add_feature("cpgsite", "cpg", [(0, 2)])
cpg2 = s3.add_feature("cpgsite", "cpg", [(5, 7)])


# In[9]:


from cogent3 import DNA

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
exon1 = s1.add_feature("exon", "A", [(10, 15)])
exon2 = s1.add_feature("exon", "B", [(30, 40)])
exon3 = s1.add_feature("exon", "C", [(45, 48)])
cds = s1.get_region_covering_all([exon1, exon2, exon3])


# In[10]:


cds.get_coordinates()


# In[11]:


not_cds = cds.get_shadow()
not_cds


# In[12]:


cds


# In[13]:


from cogent3 import make_aligned_seqs

aln1 = make_aligned_seqs(
    data=[["x", "-AAACCCCCA"], ["y", "TTTT--TTTT"]], array_align=False
)
seq_exon = aln1.get_seq("x").add_feature("exon", "A", [(3, 8)])


# In[14]:


from cogent3.core.annotation import Variable

red_data = aln1.add_annotation(
    Variable, "redline", "align", [((0, 15), 1), ((15, 30), 2), ((30, 45), 3)]
)


# In[15]:


from cogent3 import DNA

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
exon1 = s1.add_feature("exon", "A", [(10, 15)])
exon2 = s1.add_feature("exon", "B", [(30, 40)])
s1[exon1]
s1[10:15]


# In[16]:


s1[exon2]
exon2.get_slice()


# In[17]:


from cogent3 import DNA

s1 = DNA.make_seq(
    "AAGAAGAAGACCCCCAAAAAAAAAA" "TTTTTTTTTTAAAAAGGGAACCCT", name="seq1"
)
exon1 = s1.add_feature("exon", "A", [(10, 15)])
exon2 = s1.add_feature("exon", "B", [(30, 40)])
exon3 = s1.add_feature("exon", "C", [(45, 48)])
cds = s1.get_region_covering_all([exon1, exon2, exon3])
print(s1[cds])
print(s1[exon1, exon2, exon3])


# In[18]:


print(s1)
print(s1[exon1, exon2, exon3])
print(s1[exon2])
print(s1[exon3])
print(s1[exon1, exon3, exon2])


# In[19]:


s1[1:10, 9:15]
s1[exon1, exon1]


# In[20]:


print(s1.get_region_covering_all([exon3, exon3]).get_slice())


# In[21]:


print(s1[exon2])
ex2_start = exon2[0:3]
print(s1[ex2_start])
ex2_end = exon2[-3:]
print(s1[ex2_end])


# In[22]:


aln1[seq_exon]


# In[23]:


aln2 = make_aligned_seqs(
    data=[["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCC", "x")
match_exon = seq.add_feature("exon", "A", [(3, 8)])
aln2.get_seq("x").copy_annotations(seq)
copied = list(aln2.get_annotations_from_seq("x", "exon"))
copied


# In[24]:


aln2 = make_aligned_seqs(data=[["x", "-AAAA"], ["y", "TTTTT"]], array_align=False)
seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCC", "x")
match_exon = seq.add_feature("exon", "A", [(5, 8)])
aln2.get_seq("x").copy_annotations(seq)
copied = list(aln2.get_annotations_from_seq("x", "exon"))
copied
copied[0].get_slice()


# In[25]:


# new test
aln2 = make_aligned_seqs(
    data=[["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCC", "x")
match_exon = seq.add_feature("exon", "A", [(5, 8)])
aln2.get_seq("y").copy_annotations(seq)
copied = list(aln2.get_annotations_from_seq("y", "exon"))
copied


# In[26]:


aln2 = make_aligned_seqs(
    data=[["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
diff_len_seq = DNA.make_seq("CCCCCCCCCCCCCCCCCCCCCCCCCCCC", "x")
nonmatch = diff_len_seq.add_feature("repeat", "A", [(12, 14)])
aln2.get_seq("y").copy_annotations(diff_len_seq)
copied = list(aln2.get_annotations_from_seq("y", "repeat"))
copied


# In[27]:


aln_exon = aln1.get_annotations_from_any_seq("exon")
print(aln1[aln_exon])


# In[28]:


cpgsite2 = s2.get_annotations_matching("cpgsite")
print(s2[cpgsite2])
cpgsite3 = s3.get_annotations_matching("cpgsite")
s2[cpgsite3]


# In[29]:


# this test is new
dont_exist = s2.get_annotations_matching("dont_exist")
dont_exist
s2[dont_exist]


# In[30]:


aln3 = make_aligned_seqs(
    data=[["x", "C-CCCAAAAA"], ["y", "-T----TTTT"]], array_align=False
)
exon = aln3.get_seq("x").add_feature("exon", "ex1", [(0, 4)])
print(exon.get_slice())
aln_exons = list(aln3.get_annotations_from_seq("x", "exon"))
print(aln_exons)
print(aln3[aln_exons])


# In[31]:


unified = aln_exons[0].as_one_span()
print(aln3[unified])


# In[32]:


plus = DNA.make_seq("CCCCCAAAAAAAAAATTTTTTTTTTAAAGG")
plus_rpt = plus.add_feature("blah", "a", [(5, 15), (25, 28)])
print(plus[plus_rpt])
minus = plus.rc()
print(minus)
minus_rpt = minus.get_annotations_matching("blah")
print(minus[minus_rpt])


# In[33]:


from cogent3.parse.genbank import RichGenbankParser

parser = RichGenbankParser(open("data/ST_genome_part.gb"))
seq = [seq for accession, seq in parser][0]
no_cds = seq.with_masked_annotations("CDS")
print(no_cds[150:400])


# In[34]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[["x", "C-CCCAAAAAGGGAA"], ["y", "-T----TTTTG-GTT"]],
    moltype="dna",
    array_align=False,
)
exon = aln.get_seq("x").add_feature("exon", "norwegian", [(0, 4)])
print(aln.with_masked_annotations("exon", mask_char="?"))


# In[35]:


rc = aln.rc()
print(rc)
print(rc.with_masked_annotations("exon", mask_char="?"))


# In[36]:


from cogent3 import DNA

s = DNA.make_seq("CCCCAAAAAGGGAA", "x")
exon = s.add_feature("exon", "norwegian", [(0, 4)])
rpt = s.add_feature("repeat", "norwegian", [(9, 12)])
rc = s.rc()
print(s.with_masked_annotations("exon", shadow=True))
print(rc.with_masked_annotations("exon", shadow=True))
print(s.with_masked_annotations(["exon", "repeat"], shadow=True))
print(rc.with_masked_annotations(["exon", "repeat"], shadow=True))


# In[37]:


from cogent3 import DNA

s = DNA.make_seq("ATGACCCTGTAAAAAATGTGTTAACCC", name="a")
cds1 = s.add_feature("cds", "cds1", [(0, 12)])
cds2 = s.add_feature("cds", "cds2", [(15, 24)])
all_cds = s.get_annotations_matching("cds")
all_cds


# In[38]:


from cogent3.parse.genbank import RichGenbankParser

parser = RichGenbankParser(open("data/ST_genome_part.gb"))
seq = [seq for accession, seq in parser][0]
all_cds = seq.get_annotations_matching("CDS")
coding_seqs = seq.get_region_covering_all(all_cds)
coding_seqs
coding_seqs.get_slice()
noncoding_seqs = coding_seqs.get_shadow()
noncoding_seqs
noncoding_seqs.get_slice()


# In[39]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[["x", "-AAAAAAAAA"], ["y", "TTTT--TTTT"]], array_align=False
)
print(aln)
exon = aln.get_seq("x").add_feature("exon", "1", [(3, 8)])
aln_exons = aln.get_annotations_from_seq("x", "exon")
aln_exons = aln.get_annotations_from_any_seq("exon")
aln_exons


# In[40]:


from cogent3 import DNA

seq = DNA.make_seq("aaaccggttt" * 10)
v = seq.add_feature("exon", "exon", [(20, 35)])
v = seq.add_feature("repeat_unit", "repeat_unit", [(39, 49)])
v = seq.add_feature("repeat_unit", "rep2", [(49, 60)])


# In[41]:


from cogent3.util.misc import remove_files

remove_files(["annotated_%d.png" % i for i in range(1, 4)], error_on_missing=False)

