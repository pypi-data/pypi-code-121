#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
table


# In[3]:


from cogent3 import load_table

table = load_table("data/stats.tsv", sep="\t")
table


# In[4]:


from cogent3.parse.table import load_delimited

header, rows, title, legend = load_delimited("data/CerebellumDukeDNaseSeq.pk", header=False, sep="\t")
rows[:4]


# In[5]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(with_header=False, sep="\t")
rows = list(reader("data/CerebellumDukeDNaseSeq.pk"))
rows[:4]


# In[6]:


from cogent3 import load_table

table = load_table("data/stats.tsv", limit=2)
table


# In[7]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(
    lambda line: float(line[2]) <= 10, with_header=True, sep="\t"
)
table = load_table("data/stats.tsv", reader=reader, digits=1)
table


# In[8]:


reader = FilteringParser(
    lambda line: float(line[2]) <= 10, with_header=True, sep="\t", negate=True
)
table = load_table("data/stats.tsv", reader=reader, digits=1)
table


# In[9]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(columns=["Locus", "Ratio"], with_header=True, sep="\t")
table = load_table("data/stats.tsv", reader=reader)
table


# In[10]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(columns=[0, -1], with_header=True, sep="\t")
table = load_table("data/stats.tsv", reader=reader)
table


# In[11]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(with_header=True, sep="\t")
data = list(reader("data/stats.tsv"))


# In[12]:


data[:2]


# In[13]:


from cogent3 import make_table

header = ["A", "B", "C"]
rows = [range(3), range(3, 6), range(6, 9), range(9, 12)]
table = make_table(header=["A", "B", "C"], data=rows)
table


# In[14]:


from cogent3 import make_table

data = dict(A=[0, 3, 6], B=[1, 4, 7], C=[2, 5, 8])
table = make_table(data=data)
table


# In[15]:


table = make_table(header=["C", "A", "B"], data=data)
table


# In[16]:


table = load_table("data/stats.tsv", index_name="Locus")
table["NP_055852"]


# In[17]:


table["NP_055852", "Region"]


# In[18]:


from pandas import DataFrame

from cogent3 import make_table

data = dict(a=[0, 3], b=["a", "c"])
df = DataFrame(data=data)
table = make_table(data_frame=df)
table


# In[19]:


from cogent3 import make_table

table = make_table(header=["a", "b"], data=[[0, "a"], [3, "c"]])
table


# In[20]:


from cogent3 import make_table

data = dict(a=[0, 3], b=["a", "c"])
table = make_table(data=data)
table


# In[21]:


from cogent3 import make_table

d2D = {
    "edge.parent": {
        "NineBande": "root",
        "edge.1": "root",
        "DogFaced": "root",
        "Human": "edge.0",
    },
    "x": {
        "NineBande": 1.0,
        "edge.1": 1.0,
        "DogFaced": 1.0,
        "Human": 1.0,
    },
    "length": {
        "NineBande": 4.0,
        "edge.1": 4.0,
        "DogFaced": 4.0,
        "Human": 4.0,
    },
}
table = make_table(
    data=d2D,
)
table


# In[22]:


from cogent3 import make_table

table = make_table(
    header=["abcd", "data"],
    data=[[range(1, 6), "0"], ["x", 5.0], ["y", None]],
    missing_data="*",
    digits=1,
)
table


# In[23]:


from cogent3 import make_table

table = make_table()
table

