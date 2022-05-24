#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.ascii_art())


# In[3]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
tr.write("data/temp.tree")


# In[4]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
names = tr.get_node_names()
names[:4]


# In[5]:


names[4:]
names_nodes = tr.get_nodes_dict()
names_nodes["Human"]


# In[6]:


tr.get_node_matching_name("Mouse")


# In[7]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
hu = tr.get_node_matching_name("Human")
tr.name


# In[8]:


hu.name


# In[9]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
nodes = tr.get_nodes_dict()
hu = nodes["Human"]
type(hu)


# In[10]:


type(tr)


# In[11]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
nodes = tr.get_nodes_dict()
for n in nodes.items():
    print(n)


# In[12]:


for n in tr.iter_tips():
    print(n)


# In[13]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
for n in tr.iter_nontips():
    print(n.get_newick())


# In[14]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
edges = tr.get_connecting_edges("edge.1", "Human")
for edge in edges:
    print(edge.name)


# In[15]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
nodes = tr.get_nodes_dict()
hu = nodes["Human"]
mu = nodes["Mouse"]
hu.distance(mu)
hu.is_tip()


# In[16]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
nodes = tr.get_nodes_dict()
hu = nodes["Human"]
mu = nodes["Mouse"]
lca = hu.last_common_ancestor(mu)
lca


# In[17]:


type(lca)


# In[18]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
hu = tr.get_node_matching_name("Human")
for a in hu.ancestors():
    print(a.name)


# In[19]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
node = tr.get_node_matching_name("edge.1")
children = list(node.iter_tips()) + list(node.iter_nontips())
for child in children:
    print(child.name)


# In[20]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
dists = tr.get_distances()


# In[21]:


human_dists = [names for names in dists if "Human" in names]
for dist in human_dists:
    print(dist, dists[dist])


# In[22]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
tr.max_tip_tip_distance()


# In[23]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
hu = tr.get_node_matching_name("Human")
tips = hu.tips_within_distance(0.2)
for t in tips:
    print(t)


# In[24]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.rooted_at("edge.0").ascii_art())


# In[25]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.root_at_midpoint().ascii_art())


# In[26]:


print(tr.ascii_art())


# In[27]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.ascii_art())


# In[28]:


print(tr.rooted_with_tip("Mouse").ascii_art())


# In[29]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
tr.get_newick()


# In[30]:


tr.get_newick(with_distances=True)


# In[31]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
xml = tr.get_xml()
for line in xml.splitlines():
    print(line)


# In[32]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.ascii_art())


# In[33]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
for t in tr.preorder():
    print(t.get_newick())


# In[34]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
for t in tr.postorder():
    print(t.get_newick())


# In[35]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
for tip in tr.iter_nontips():
    tip_names = tip.get_tip_names()
    print(tip_names)
    sub_tree = tr.get_sub_tree(tip_names)
    print(sub_tree.ascii_art())


# In[36]:


from cogent3.util.misc import remove_files

remove_files(["data/temp.tree", "data/temp.pdf"], error_on_missing=False)


# In[37]:


from cogent3 import make_tree

simple_tree_string = "(B:0.2,(D:0.4)E:0.5)F;"
simple_tree = make_tree(simple_tree_string)
print(simple_tree.ascii_art())


# In[38]:


simple_tree.prune()
print(simple_tree.ascii_art())


# In[39]:


print(simple_tree)


# In[40]:


from cogent3 import load_tree

tr1 = load_tree("data/test.tree")
print(tr1.get_newick())


# In[41]:


tr2 = tr1.unrooted_deepcopy()
print(tr2.get_newick())


# In[42]:


from cogent3 import load_tree

tree_string = "(B:0.2,H:0.2,(C:0.3,D:0.4,E:0.1)F:0.5)G;"
tr = make_tree(tree_string)
print(tr.ascii_art())


# In[43]:


print(tr.bifurcating().ascii_art())


# In[44]:


from cogent3 import load_tree

tr = load_tree("data/test.tree")
print(tr.ascii_art())


# In[45]:


print(tr.balanced().ascii_art())


# In[46]:


from cogent3 import load_tree

tr1 = make_tree("(B:0.2,(C:0.2,D:0.2)F:0.2)G;")
tr2 = make_tree("((C:0.1,D:0.1)F:0.1,B:0.1)G;")
tr1.same_topology(tr2)


# In[47]:


from cogent3 import load_tree

tr = make_tree("(B:0.2,(C:0.3,D:0.4)F:0.5)G;")
print(tr.ascii_art())


# In[48]:


tr.set_tip_distances()
for t in tr.preorder():
    print(t.name, t.TipDistance)


# In[49]:


from cogent3 import load_tree

tr = make_tree("(B:0.2,(C:0.3,D:0.4)F:0.5)G;")
print(tr)


# In[50]:


tr.scale_branch_lengths()
print(tr)


# In[51]:


from cogent3 import load_tree

tr = make_tree("(B:3,(C:2,D:4)F:5)G;")
d, tips = tr.tip_to_tip_distances()
for i, t in enumerate(tips):
    print(t.name, d[i])


# In[52]:


from cogent3 import load_tree

tr1 = make_tree("(B:2,(C:3,D:4)F:5)G;")
tr2 = make_tree("(C:2,(B:3,D:4)F:5)G;")
tr1.compare_by_tip_distances(tr2)

