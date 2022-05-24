#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, make_tree, make_table
from cogent3.evolve.models import HKY85
from cogent3.recalculation.scope import EACH, ALL
from cogent3.maths.stats import chisqprob

aln = load_aligned_seqs("data/long_testseqs.fasta")
half = len(aln) // 2
aln1 = aln[:half]
aln2 = aln[half:]


# In[3]:


loci_names = ["1st-half", "2nd-half"]
loci = [aln1, aln2]
tree = make_tree(tip_names=aln.names)
mod = HKY85()


# In[4]:


lf = mod.make_likelihood_function(tree, loci=loci_names, digits=2, space=3)
lf.set_param_rule("length", is_independent=False)
lf.set_param_rule("kappa", loci=ALL)
lf.set_alignment(loci)
lf.optimise(show_progress=False)
lf


# In[5]:


all_lnL = lf.lnL
all_nfp = lf.nfp
lf.set_param_rule("kappa", loci=EACH)
lf.optimise(show_progress=False)
lf


# In[6]:


each_lnL = lf.lnL
each_nfp = lf.nfp
LR = 2 * (each_lnL - all_lnL)
df = each_nfp - all_nfp


# In[7]:


make_table(
    header=["LR", "df", "p"], rows=[[LR, df, chisqprob(LR, df)]], digits=2, space=3,
)

