#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.evolve.substitution_model import TimeReversibleNucleotide
from cogent3 import load_tree


# In[3]:


model = TimeReversibleNucleotide(equal_motif_probs=True)
tree = load_tree("data/test.tree")
lf = model.make_likelihood_function(tree)
lf.set_param_rule("length", value=0.6, is_constant=True)
aln1 = lf.simulate_alignment(sequence_length=10000)
lf.set_param_rule("length", value=0.2, is_constant=True)
aln2 = lf.simulate_alignment(sequence_length=10000)
aln3 = aln1 + aln2


# In[4]:


model = TimeReversibleNucleotide(
    equal_motif_probs=True, ordered_param="rate", distribution="free"
)
lf = model.make_likelihood_function(tree, bins=2, digits=2, space=3)
lf.set_alignment(aln3)
lf.optimise(local=True, max_restarts=2, show_progress=False)


# In[5]:


bprobs = [t for t in lf.get_statistics() if "bin" in t.title][0]
bprobs


# In[6]:


model = TimeReversibleNucleotide(
    equal_motif_probs=True, ordered_param="rate", distribution="gamma"
)
lf = model.make_likelihood_function(tree, bins=4)
lf.set_param_rule("bprobs", is_constant=True)
lf.set_alignment(aln3)
lf.optimise(local=True, max_restarts=2, show_progress=False)

