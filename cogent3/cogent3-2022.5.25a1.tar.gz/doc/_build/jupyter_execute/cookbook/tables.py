#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


import set_working_directory


# In[3]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
table


# In[4]:


from cogent3 import load_table

table = load_table("data/stats.tsv", sep="\t")
table


# In[5]:


from cogent3.parse.table import load_delimited

header, rows, title, legend = load_delimited("data/CerebellumDukeDNaseSeq.pk", header=False, sep="\t")
rows[:4]


# In[6]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(with_header=False, sep="\t")
rows = list(reader("data/CerebellumDukeDNaseSeq.pk"))
rows[:4]


# In[7]:


from cogent3 import load_table

table = load_table("data/stats.tsv", limit=2)
table


# In[8]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(
    lambda line: float(line[2]) <= 10, with_header=True, sep="\t"
)
table = load_table("data/stats.tsv", reader=reader, digits=1)
table


# In[9]:


reader = FilteringParser(
    lambda line: float(line[2]) <= 10, with_header=True, sep="\t", negate=True
)
table = load_table("data/stats.tsv", reader=reader, digits=1)
table


# In[10]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(columns=["Locus", "Ratio"], with_header=True, sep="\t")
table = load_table("data/stats.tsv", reader=reader)
table


# In[11]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(columns=[0, -1], with_header=True, sep="\t")
table = load_table("data/stats.tsv", reader=reader)
table


# In[12]:


from cogent3.parse.table import FilteringParser

reader = FilteringParser(with_header=True, sep="\t")
data = list(reader("data/stats.tsv"))


# In[13]:


data[:2]


# In[14]:


from cogent3 import make_table

header = ["A", "B", "C"]
rows = [range(3), range(3, 6), range(6, 9), range(9, 12)]
table = make_table(header=["A", "B", "C"], data=rows)
table


# In[15]:


from cogent3 import make_table

data = dict(A=[0, 3, 6], B=[1, 4, 7], C=[2, 5, 8])
table = make_table(data=data)
table


# In[16]:


table = make_table(header=["C", "A", "B"], data=data)
table


# In[17]:


table = load_table("data/stats.tsv", index_name="Locus")
table["NP_055852"]


# In[18]:


table["NP_055852", "Region"]


# In[19]:


from pandas import DataFrame

from cogent3 import make_table

data = dict(a=[0, 3], b=["a", "c"])
df = DataFrame(data=data)
table = make_table(data_frame=df)
table


# In[20]:


from cogent3 import make_table

table = make_table(header=["a", "b"], data=[[0, "a"], [3, "c"]])
table


# In[21]:


from cogent3 import make_table

data = dict(a=[0, 3], b=["a", "c"])
table = make_table(data=data)
table


# In[22]:


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


# In[23]:


from cogent3 import make_table

table = make_table(
    header=["abcd", "data"],
    data=[[range(1, 6), "0"], ["x", 5.0], ["y", None]],
    missing_data="*",
    digits=1,
)
table


# In[24]:


from cogent3 import make_table

table = make_table()
table


# In[25]:


from cogent3 import make_table

table = make_table()
table.columns["a"] = [1, 3, 5]
table.columns["b"] = [2, 4, 6]
table


# In[26]:


from cogent3 import make_table

data = dict(a=[0, 3], b=["a", "c"])
table = make_table(data=data, title="Sample title", legend="a legend")
table


# In[27]:


data = dict(a=[0, 3], b=["a", "c"])
table = make_table(data=data)
table.title = "My title"
table


# In[28]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
for row in table:
    print(row)
    break


# In[29]:


for row in table:
    print(row["Locus"])


# In[30]:


from cogent3 import make_table

data = dict(a=[0, 3, 5], b=["a", "c", "d"])
table = make_table(data=data)
table.shape[0] == 3


# In[31]:


table.shape[1] == 2


# In[32]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
table.columns


# In[33]:


table.columns["Region"]


# In[34]:


for name in table.columns:
    print(name)


# In[35]:


table = load_table("data/stats.tsv")
table


# In[36]:


table[:2, "Region":]


# In[37]:


table = load_table("data/stats.tsv")
table[:2, :1]


# In[38]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
table.format_column("Ratio", "%.1e")
table


# In[39]:


table = load_table("data/stats.tsv", digits=1, space=2)
table


# In[40]:


table.space = "    "
table


# In[41]:


from cogent3 import make_table

h = ["name", "A/C", "A/G", "A/T", "C/A"]
rows = [["tardigrade", 0.0425, 0.1424, 0.0226, 0.0391]]
wrap_table = make_table(header=h, data=rows, max_width=30)
wrap_table


# In[42]:


wrap_table = make_table(header=h, data=rows, max_width=30, index_name="name")
wrap_table


# In[43]:


table = make_table(data=dict(a=list(range(10)), b=list(range(10))))
table.head()


# In[44]:


table.head(2)


# In[45]:


table.tail()


# In[46]:


table.tail(1)


# In[47]:


table.set_repr_policy(random=3)
table


# In[48]:


table.set_repr_policy(head=2, tail=3)
table


# In[49]:


table = load_table("data/stats.tsv")
print(table.header)
table = table.with_new_header("Ratio", "Stat")
print(table.header)


# In[50]:


from cogent3 import make_table

table = make_table()
table


# In[51]:


table.columns["a"] = [1, 3, 5]
table.columns["b"] = [2, 4, 6]
table


# In[52]:


table = load_table("data/stats.tsv")
table = table.with_new_column(
    "LargeCon",
    lambda r_v: r_v[0] == "Con" and r_v[1] > 10.0,
    columns=["Region", "Ratio"],
)
table


# In[53]:


table = load_table("data/stats.tsv")
table.array


# In[54]:


table = load_table("data/stats.tsv")
locus = table.tolist("Locus")
locus


# In[55]:


table.columns["Locus"].tolist()


# In[56]:


table = load_table("data/stats.tsv")
rows = table.tolist(["Region", "Locus"])
rows


# In[57]:


table = load_table("data/stats.tsv")
table.to_dict()


# In[58]:


table = load_table("data/stats.tsv")
table.columns.to_dict()


# In[59]:


table = load_table("data/stats.tsv")
df = table.to_dataframe()
df


# In[60]:


df = table.to_dataframe(categories="Region")


# In[61]:


table = make_table(data={"Ts": [31, 58], "Tv": [36, 138], "": ["syn", "nsyn"]}, index_name="")
table


# In[62]:


contingency = table.to_categorical(["Ts", "Tv"])
contingency


# In[63]:


g_test = contingency.G_independence()
g_test


# In[64]:


table = make_table(data={"Ts": [31, 58], "Tv": [36, 138], "": ["syn", "nsyn"]})
contingency = table.to_categorical(["Ts", "Tv"], index_name="")


# In[65]:


table1 = load_table("data/stats.tsv")
table2 = load_table("data/stats.tsv")
table = table1.appended(None, table2)
table


# In[66]:


table1.title = "Data1"
table2.title = "Data2"
table = table1.appended("Data#", table2, title="")
table


# In[67]:


table = load_table("data/stats.tsv")
table.summed("Ratio")


# In[68]:


table.columns["Ratio"].sum()


# In[69]:


from cogent3 import make_table

all_numeric = make_table(
    header=["A", "B", "C"], data=[range(3), range(3, 6), range(6, 9), range(9, 12)]
)
all_numeric


# In[70]:


all_numeric.summed()


# In[71]:


all_numeric.summed(col_sum=False)


# In[72]:


mixed = make_table(
    header=["A", "B", "C"], data=[["*", 1, 2], [3, "*", 5], [6, 7, "*"]]
)
mixed


# In[73]:


mixed.summed(strict=False)


# In[74]:


mixed.summed(col_sum=False, strict=False)


# In[75]:


table = load_table("data/stats.tsv")
sub_table = table.filtered(lambda x: x < 10.0, columns="Ratio")
sub_table


# In[76]:


sub_table = table.filtered("Ratio < 10.0")
sub_table


# In[77]:


sub_table = table.filtered("Ratio < 10.0 and Region == 'NonCon'")
sub_table


# In[78]:


big_numeric = all_numeric.filtered_by_column(lambda x: sum(x) > 20)
big_numeric


# In[79]:


table = load_table("data/stats.tsv")
table.sorted(columns="Ratio")


# In[80]:


table.sorted(columns="Ratio", reverse="Ratio")


# In[81]:


table.sorted(columns=["Region", "Ratio"], reverse="Ratio")


# In[82]:


table = load_table("data/stats.tsv")
raw = table.tolist("Region")
raw


# In[83]:


table = load_table("data/stats.tsv")
raw = table.tolist(["Locus", "Region"])
raw


# In[84]:


table = load_table("data/stats.tsv")
assert table.distinct_values("Region") == set(["NonCon", "Con"])


# In[85]:


table = load_table("data/stats.tsv")
assert table.count("Region == 'NonCon' and Ratio > 1") == 1


# In[86]:


from cogent3 import make_table

table = make_table(
    data=dict(A=["a", "b", "b", "b", "a"], B=["c", "c", "c", "c", "d"])
)
unique = table.count_unique("A")
type(unique)


# In[87]:


unique


# In[88]:


unique = table.count_unique(["A", "B"])
unique


# In[89]:


r = unique.to_table()
r


# In[90]:


rows = [
    ["NP_004893", True],
    ["NP_005079", True],
    ["NP_005500", False],
    ["NP_055852", False],
]
region_type = make_table(header=["Locus", "LargeCon"], data=rows)
stats_table = load_table("data/stats.tsv")
new = stats_table.joined(region_type, columns_self="Locus")
new


# In[91]:


from cogent3 import make_table

header = ["#OTU ID", "14SK041", "14SK802"]
rows = [
    [-2920, "332", 294],
    [-1606, "302", 229],
    [-393, 141, 125],
    [-2109, 138, 120],
]
table = make_table(header=header, rows=rows)
table


# In[92]:


tp = table.transposed(new_column_name="sample", select_as_header="#OTU ID")
tp


# In[93]:


from cogent3 import load_table

table = load_table("data/stats.tsv", format="md")
print(table)


# In[94]:


from cogent3 import load_table

table = load_table("data/stats.tsv", format="tex")
print(table)


# In[95]:


table = load_table("data/stats.tsv")
print(table.to_markdown(justify="ccr"))


# In[96]:


table = load_table(
    "data/stats.tsv", title="Some stats.", legend="Derived from something."
)
print(table.to_latex(justify="ccr", label="tab:table1"))


# In[97]:


table = load_table(
    "data/stats.tsv", title="Some stats.", legend="Derived from something."
)
print(table.to_rst(csv_table=True))


# In[98]:


table = load_table(
    "data/stats.tsv", title="Some stats.", legend="Derived from something."
)
print(table.to_rst())


# In[99]:


table = load_table("data/stats.tsv")
print(table.to_string(format="latex"))


# In[100]:


rows = [
    ["1", 100, 101, 1.123],
    ["1", 101, 102, 1.123],
    ["1", 102, 103, 1.123],
    ["1", 103, 104, 1.123],
    ["1", 104, 105, 1.123],
    ["1", 105, 106, 1.123],
    ["1", 106, 107, 1.123],
    ["1", 107, 108, 1.123],
    ["1", 108, 109, 1],
    ["1", 109, 110, 1],
    ["1", 110, 111, 1],
    ["1", 111, 112, 1],
    ["1", 112, 113, 1],
    ["1", 113, 114, 1],
    ["1", 114, 115, 1],
    ["1", 115, 116, 1],
    ["1", 116, 117, 1],
    ["1", 117, 118, 1],
    ["1", 118, 119, 2],
    ["1", 119, 120, 2],
    ["1", 120, 121, 2],
    ["1", 150, 151, 2],
    ["1", 151, 152, 2],
    ["1", 152, 153, 2],
    ["1", 153, 154, 2],
    ["1", 154, 155, 2],
    ["1", 155, 156, 2],
    ["1", 156, 157, 2],
    ["1", 157, 158, 2],
    ["1", 158, 159, 2],
    ["1", 159, 160, 2],
    ["1", 160, 161, 2],
]
bgraph = make_table(header=["chrom", "start", "end", "value"], rows=rows)


# In[101]:


bgraph.head()


# In[102]:


print(
    bgraph.to_string(
        format="bedgraph",
        name="test track",
        description="test of bedgraph",
        color=(255, 0, 0),
        digits=0,
    )
)


# In[103]:


from cogent3 import load_table

table = load_table("data/stats.tsv")
straight_html = table.to_html()


# In[104]:


from cogent3.format.table import known_formats

known_formats


# In[105]:


table.write("stats_tab.tex", justify="ccr", label="tab:table1")


# In[106]:


table = load_table("data/stats.tsv")
table.write("stats_tab.txt", sep="\t")


# In[107]:


import pathlib

for name in ("stats_tab.txt", "stats_tab.tex"):
    p = pathlib.Path(name)
    if p.exists():
        p.unlink()

