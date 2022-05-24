#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3.core.tree import PhyloNode
from cogent3 import load_tree, make_tree
from cogent3.parse.tree import DndParser


# In[2]:


simple_tree_string = "(B:0.2,(C:0.3,D:0.4)E:0.5)F;"
complex_tree_string = "(((363564 AB294167.1 Alkalibacterium putridalgicola:0.0028006,55874 AB083411.1 Marinilactibacillus psychrotolerans:0.0022089):0.40998,(15050 Y10772.1 Facklamia hominis:0.32304,(132509 AY707780.1 Aerococcus viridans:0.58815,((143063 AY879307.1 Abiotrophia defectiva:0.5807,83619 AB042060.1 Bacillus schlegelii:0.23569):0.03586,169722 AB275483.1 Fibrobacter succinogenes:0.38272):0.06516):0.03492):0.14265):0.63594,(3589 M62687.1 Fibrobacter intestinalis:0.65866,314063 CP001146.1 Dictyoglomus thermophilum:0.38791):0.32147,276579 EU652053.1 Thermus scotoductus:0.57336);"
simple_tree = make_tree(simple_tree_string)
complex_tree = DndParser(complex_tree_string, PhyloNode)


# In[3]:


print(simple_tree.ascii_art())


# In[4]:


A_node = PhyloNode(name="A", Length=0.1)


# In[5]:


print(simple_tree.children)


# In[6]:


simple_tree.children[1].remove("C")


# In[7]:


simple_tree.children[1].insert(0, A_node)


# In[8]:


print(simple_tree.ascii_art())


# In[9]:


simple_tree.children[1].remove("A")
print(simple_tree.ascii_art())


# In[10]:


simple_tree.prune()
print(simple_tree.ascii_art())


# In[11]:


for n in complex_tree.iter_tips():
    n.name = n.name.split()[2] + " " + n.name.split()[3]


# In[12]:


print(complex_tree.ascii_art(show_internal=False))


# In[13]:


tips = complex_tree.tips()


# In[14]:


tips_to_delete = []
AEROCOCCUS_INDEX = 3
for n in tips:
    if tips[AEROCOCCUS_INDEX].distance(n) > 1.8:
        tips_to_delete.append(n)


# In[15]:


for n in tips_to_delete:
    n.parent.remove(n)
    complex_tree.prune()


# In[16]:


print(complex_tree.ascii_art(show_internal=False))

