#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import make_aligned_seqs, make_unaligned_seqs

dna = {"seq1": "ATGACC", "seq2": "ATCGCC"}
seqs = make_aligned_seqs(data=dna, moltype="dna")
print(type(seqs))
seqs = make_unaligned_seqs(dna, moltype="dna")
print(type(seqs))


# In[3]:


from cogent3 import make_aligned_seqs

dna = {"seq1": "ATGACC", "seq2": "ATCGCC"}
seqs = make_aligned_seqs(data=dna, moltype="dna", array_align=True)
print(type(seqs))
print(seqs)


# In[4]:


from cogent3 import load_unaligned_seqs

seqs = load_unaligned_seqs("data/test.paml")
print(seqs)


# In[5]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    [("seq1", "ATGAA------"), ("seq2", "ATG-AGTGATG"), ("seq3", "AT--AG-GATG")],
    moltype="dna",
)
print(aln)
new_seqs = make_aligned_seqs(
    [("seq0", "ATG-AGT-AGG"), ("seq4", "ATGCC------")], moltype="dna"
)
new_aln = aln.add_seqs(new_seqs)
print(new_aln)


# In[6]:


new_aln = aln.add_seqs(new_seqs, before_name="seq2")
print(new_aln)
new_aln = aln.add_seqs(new_seqs, after_name="seq2")
print(new_aln)


# In[7]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    [("seq1", "ATGAA------"), ("seq2", "ATG-AGTGATG"), ("seq3", "AT--AG-GATG")],
    moltype="dna",
)
ref_aln = make_aligned_seqs(
    [("seq3", "ATAGGATG"), ("seq0", "ATG-AGCG"), ("seq4", "ATGCTGGG")],
    moltype="dna",
)
new_aln = aln.add_from_ref_aln(ref_aln)
print(new_aln)


# In[8]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    [("seq1", "ATGAA---TG-"), ("seq2", "ATG-AGTGATG"), ("seq3", "AT--AG-GATG")],
    moltype="dna",
)
new_aln = aln.get_degapped_relative_to("seq1")
print(new_aln)


# In[9]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    [("seq1", "ATGAA------"), ("seq2", "ATG-AGTGATG"), ("seq3", "AT--AG-GATG")],
    moltype="dna",
    array_align=False,
)
seq = aln.get_seq("seq1")
seq.name
type(seq)
seq.is_gapped()


# In[10]:


seq = aln.get_gapped_seq("seq1")
seq.is_gapped()
print(seq)


# In[11]:


aln.names
aln.names


# In[12]:


from cogent3 import load_unaligned_seqs, load_aligned_seqs

fn = "data/long_testseqs.fasta"
seqs = load_unaligned_seqs(fn, moltype="dna")
my_seq = seqs.seqs[0]
my_seq[:24]
str(my_seq[:24])
type(my_seq)
aln = load_aligned_seqs(fn, moltype="dna")
aln.seqs[0][:24]
print(aln.seqs[0][:24])


# In[13]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/test.paml", moltype="dna")
aln.names
new = aln.take_seqs(["Human", "HowlerMon"])
new.names


# In[14]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/test.paml", array_align=False, moltype="dna")
seq = aln.get_seq("Human")
new = aln.take_seqs(["Human", "HowlerMon"])
id(new.get_seq("Human")) == id(aln.get_seq("Human"))


# In[15]:


from cogent3 import load_unaligned_seqs
from cogent3.core.alignment import Alignment

seq = load_unaligned_seqs("data/test.paml")
aln = Alignment(seq)
fasta_1 = seq
fasta_2 = aln
assert fasta_1 == fasta_2


# In[16]:


from cogent3 import make_aligned_seqs

data = [("a", "ACG---"), ("b", "CCTGGG")]
aln = make_aligned_seqs(data=data)
dna = aln.to_dna()
dna


# In[17]:


from cogent3 import make_aligned_seqs

data = [("a", "ACG---"), ("b", "CCUGGG")]
aln = make_aligned_seqs(data=data)
rna = aln.to_rna()
rna


# In[18]:


from cogent3 import make_aligned_seqs

data = [("x", "TYV"), ("y", "TE-")]
aln = make_aligned_seqs(data=data)
prot = aln.to_protein()
prot


# In[19]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta")
degapped = aln.degap()
print(type(degapped))


# In[20]:


from cogent3 import make_aligned_seqs

dna = {"seq1": "ATGACC", "seq2": "ATCGCC"}
aln = make_aligned_seqs(data=dna, moltype="dna")
aln.write("sample.fasta")


# In[21]:


aln.write("sample", format="fasta")


# In[22]:


from cogent3.util.misc import remove_files

remove_files(["sample", "sample.fasta"], error_on_missing=False)


# In[23]:


from cogent3 import load_aligned_seqs
from cogent3.core.alignment import Alignment

seq = load_aligned_seqs("data/long_testseqs.fasta")
aln = Alignment(seq)
fasta_align = aln


# In[24]:


from cogent3 import load_aligned_seqs
from cogent3.core.alignment import Alignment

seq = load_aligned_seqs("data/test.paml")
aln = Alignment(seq)
got = aln.to_phylip()
print(got)


# In[25]:


from cogent3 import load_aligned_seqs
from cogent3.core.alignment import Alignment

seq = load_aligned_seqs("data/test.paml")
aln = Alignment(seq)
string_list = aln.to_dict().values()


# In[26]:


from cogent3 import load_aligned_seqs

fn = "data/long_testseqs.fasta"
aln = load_aligned_seqs(fn, moltype="dna")
print(aln[:24])


# In[27]:


from cogent3 import load_unaligned_seqs

fn = "data/long_testseqs.fasta"
seqs = load_unaligned_seqs(fn)
print(seqs[:24])


# In[28]:


from cogent3 import load_aligned_seqs

seq = load_aligned_seqs("data/test.paml")
column_four = aln[3]


# In[29]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta")
region = aln[50:70]


# In[30]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta")
col = aln[113:115].iter_positions()
type(col)
list(col)


# In[31]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data={"seq1": "ATGATGATG---", "seq2": "ATGATGATGATG"}, array_align=False
)
list(range(len(aln))[2::3])
indices = [(i, i + 1) for i in range(len(aln))[2::3]]
indices
pos3 = aln.add_feature("pos3", "pos3", indices)
pos3 = pos3.get_slice()
print(pos3)


# In[32]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data={"seq1": "ATGATGATG---", "seq2": "ATGATGATGATG"}, array_align=True
)
pos3 = aln[2::3]
print(pos3)


# In[33]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data={"seq1": "ACGTAA---", "seq2": "ACGACA---", "seq3": "ACGCAATGA"},
    moltype="dna",
)
new = aln.trim_stop_codons()
print(new)


# In[34]:


aln = make_aligned_seqs(
    data={
        "seq1": "ACGTAA---",
        "seq2": "ACGAC----",  # terminal codon incomplete
        "seq3": "ACGCAATGA",
    },
    moltype="dna",
)
new = aln.trim_stop_codons(allow_partial=True)
print(new)


# In[35]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAAGGTG---"),
        ("seq2", "ATGAAGGTGATG"),
        ("seq3", "ATGAAGGNGATG"),
    ],
    moltype="dna",
)


# In[36]:


nucs = aln.no_degenerates()
print(nucs)


# In[37]:


trinucs = aln.no_degenerates(motif_length=3)
print(trinucs)


# In[38]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta")
pos = aln.variable_positions()
just_variable_aln = aln.take_positions(pos)
print(just_variable_aln[:10])


# In[39]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta")
pos = aln.variable_positions()
just_constant_aln = aln.take_positions(pos, negate=True)
print(just_constant_aln[:10])


# In[40]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta")
variable_codons = aln.filtered(
    lambda x: len(set(map(tuple, x))) > 1, motif_length=3
)
print(just_variable_aln[:9])


# In[41]:


aln = aln.to_type(array_align=False)
variable_codons = aln.filtered(lambda x: len(set("".join(x))) > 1, motif_length=3)
print(just_variable_aln[:9])


# In[42]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta")
aln.take_seqs(["Human", "Mouse"])


# In[43]:


aln.take_seqs(["Human", "Mouse"], negate=True)


# In[44]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAAGGTG---"),
        ("seq2", "ATGAAGGTGATG"),
        ("seq3", "ATGAAGGNGATG"),
    ],
    moltype="dna",
)

def no_N_chars(s):
    return "N" not in s

aln.take_seqs_if(no_N_chars)


# In[45]:


aln.take_seqs_if(no_N_chars, negate=True)


# In[46]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAAGGTG---"),
        ("seq2", "ATGAAGGTGATG"),
        ("seq3", "ATGAAGGNGATG"),
    ],
    moltype="dna",
)
counts = aln.counts()
print(counts)
counts = aln.counts(motif_length=3)
print(counts)
counts = aln.counts(include_ambiguity=True)
print(counts)


# In[47]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta", moltype="dna")
motif_probs = aln.get_motif_probs()
print(motif_probs)


# In[48]:


from cogent3 import load_aligned_seqs, DNA

trinuc_alphabet = DNA.alphabet.get_word_alphabet(3)
aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta", moltype="dna")
motif_probs = aln.get_motif_probs(alphabet=trinuc_alphabet)
for m in sorted(motif_probs, key=lambda x: motif_probs[x], reverse=True):
    print("%s  %.3f" % (m, motif_probs[m]))


# In[49]:


aln = make_aligned_seqs(data=[("a", "AACAAC"), ("b", "AAGAAG")], moltype="dna")
motif_probs = aln.get_motif_probs()
assert motif_probs["T"] == 0.0
motif_probs = aln.get_motif_probs(pseudocount=1e-6)
assert 0 < motif_probs["T"] <= 1e-6


# In[50]:


seqs = [("a", "AACGTAAG"), ("b", "AACGTAAG")]
aln = make_aligned_seqs(data=seqs, moltype="dna")
dinuc_alphabet = DNA.alphabet.get_word_alphabet(2)
motif_probs = aln.get_motif_probs(alphabet=dinuc_alphabet)
assert motif_probs["AA"] == 0.25


# In[51]:


seqs = [("my_seq", "AAAGTAAG")]
aln = make_aligned_seqs(data=seqs, moltype="dna")
my_seq = aln.get_seq("my_seq")
my_seq.count("AA")
"AAA".count("AA")
"AAAA".count("AA")


# In[52]:


from cogent3 import make_seq

seq = make_seq(moltype="dna", seq="AAAGTAAG")
seq
di_nucs = [seq[i : i + 2] for i in range(len(seq) - 1)]
sum([nn == "AA" for nn in di_nucs])


# In[53]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta")
col = aln[113:115].iter_positions()
c1, c2 = list(col)
c1, c2
list(filter(lambda x: x == "-", c1))
list(filter(lambda x: x == "-", c2))


# In[54]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/primate_cdx2_promoter.fasta")
for column in aln[113:150].iter_positions():
    ungapped = list(filter(lambda x: x == "-", column))
    gap_fraction = len(ungapped) * 1.0 / len(column)
    print(gap_fraction)


# In[55]:


from cogent3 import make_aligned_seqs

aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAAGG-TG--"),
        ("seq2", "ATG-AGGTGATG"),
        ("seq3", "ATGAAG--GATG"),
    ],
    moltype="dna",
)
seq_to_aln_map = aln.get_gapped_seq("seq1").gap_maps()[0]


# In[56]:


seq_to_aln_map[3]
seq_to_aln_map[8]


# In[57]:


aln_to_seq_map = aln.get_gapped_seq("seq1").gap_maps()[1]
aln_to_seq_map[3]
aln_to_seq_map[8]


# In[58]:


seq_pos = aln_to_seq_map[7]


# In[59]:


aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAA---TG-"),
        ("seq2", "ATG-AGTGATG"),
        ("seq3", "AT--AG-GATG"),
    ],
    moltype="dna",
)
print(aln.omit_gap_runs(2))


# In[60]:


aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAA---TG-"),
        ("seq2", "ATG-AGTGATG"),
        ("seq3", "AT--AG-GATG"),
    ],
    moltype="dna",
)
print(aln.omit_gap_pos(0.40))


# In[61]:


aln = make_aligned_seqs(
    data=[
        ("seq1", "ATGAA------"),
        ("seq2", "ATG-AGTGATG"),
        ("seq3", "AT--AG-GATG"),
    ],
    moltype="dna",
)
filtered_aln = aln.omit_gap_seqs(0.50)
print(filtered_aln)


# In[62]:


print(filtered_aln.omit_gap_pos())

