#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta", moltype="dna")
type(aln)


# In[3]:


aln.info.source


# In[4]:


from cogent3 import load_unaligned_seqs

seqs = load_unaligned_seqs("data/long_testseqs.fasta", moltype="dna")
type(seqs)


# In[5]:


from cogent3 import load_aligned_seqs

aln = load_aligned_seqs("data/long_testseqs.fasta", moltype="dna", format="fasta")
aln


# In[6]:


from cogent3 import make_aligned_seqs

protein_seqs = [">seq1", "DEKQL-RG", ">seq2", "DDK--SRG"]
proteins_loaded = make_aligned_seqs(protein_seqs)
proteins_loaded.moltype
print(proteins_loaded)
proteins_loaded = make_aligned_seqs(protein_seqs, moltype="protein")
print(proteins_loaded)


# In[7]:


from cogent3 import make_aligned_seqs

seqs = {"seq1": "AATCG-A", "seq2": "AATCGGA"}
seqs_loaded = make_aligned_seqs(seqs)


# In[8]:


from cogent3 import make_aligned_seqs

seqs = [">seq1", "AATCG-A", ">seq2", "AATCGGA"]
seqs_loaded = make_aligned_seqs(seqs)
print(seqs_loaded)


# In[9]:


from cogent3 import make_aligned_seqs

DNA_seqs = [
    ">sample1 Mus musculus",
    "AACCTGC--C",
    ">sample2 Gallus gallus",
    "AAC-TGCAAC",
]
loaded_seqs = make_aligned_seqs(
    DNA_seqs, moltype="dna", label_to_name=lambda x: x.split()[0]
)
loaded_seqs


# In[10]:


from cogent3 import make_unaligned_seqs

seqs = {"seq1": "AATCA", "seq2": "AATCGGA"}
seqs = make_unaligned_seqs(data=seqs, moltype="dna")
seqs


# In[11]:


from cogent3.parse.fasta import MinimalFastaParser

f = open("data/long_testseqs.fasta")
seqs = [(name, seq) for name, seq in MinimalFastaParser(f)]
seqs


# In[12]:


from cogent3.parse.fasta import LabelParser

def latin_to_common(latin):
    return {"Homo sapiens": "human", "Pan troglodtyes": "chimp"}[latin]

label_parser = LabelParser(
    "%(species)s", [[1, "species", latin_to_common]], split_with=":"
)
for label in ">abcd:Homo sapiens:misc", ">abcd:Pan troglodtyes:misc":
    label = label_parser(label)
    print(label, type(label))


# In[13]:


from cogent3.parse.fasta import MinimalFastaParser, LabelParser

fasta_data = [
    ">gi|10047090|ref|NP_055147.1| small muscle protein, X-linked [Homo sapiens]",
    "MNMSKQPVSNVRAIQANINIPMGAFRPGAGQPPRRKECTPEVEEGVPPTSDEEKKPIPGAKKLPGPAVNL",
    "SEIQNIKSELKYVPKAEQ",
    ">gi|10047092|ref|NP_037391.1| neuronal protein [Homo sapiens]",
    "MANRGPSYGLSREVQEKIEQKYDADLENKLVDWIILQCAEDIEHPPPGRAHFQKWLMDGTVLCKLINSLY",
    "PPGQEPIPKISESKMAFKQMEQISQFLKAAETYGVRTTDIFQTVDLWEGKDMAAVQRTLMALGSVAVTKD",
]
label_to_name = LabelParser(
    "%(ref)s",
    [[1, "gi", str], [3, "ref", str], [4, "description", str]],
    split_with="|",
)
for name, seq in MinimalFastaParser(fasta_data, label_to_name=label_to_name):
    print(name)
    print(name.info.gi)
    print(name.info.description)

