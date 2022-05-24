#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.evolve.substitution_model import TimeReversibleNucleotide, predicate
from cogent3 import load_aligned_seqs, load_tree
from cogent3.maths.stats import chisqprob


# In[3]:


aln = load_aligned_seqs("data/long_testseqs.fasta")
tree = load_tree("data/test.tree")


# In[4]:


MotifChange = predicate.MotifChange
treat_gap = dict(recode_gaps=True, model_gaps=False)
kappa = (~MotifChange("R", "Y")).aliased("kappa")
model = TimeReversibleNucleotide(predicates=[kappa], **treat_gap)


# In[5]:


lf_one = model.make_likelihood_function(tree, digits=2, space=3)
lf_one.set_alignment(aln)
lf_one.optimise(show_progress=False)
lnL_one = lf_one.get_log_likelihood()
df_one = lf_one.get_num_free_params()
lf_one


# In[6]:


bin_submod = TimeReversibleNucleotide(
    predicates=[kappa], ordered_param="rate", distribution="gamma", **treat_gap
)
lf_bins = bin_submod.make_likelihood_function(
    tree, bins=2, sites_independent=True, digits=2, space=3
)
lf_bins.set_param_rule("bprobs", is_constant=True)
lf_bins.set_alignment(aln)
lf_bins.optimise(local=True, show_progress=False)
lnL_bins = lf_bins.get_log_likelihood()
df_bins = lf_bins.get_num_free_params()
assert df_bins == 9
lf_bins


# In[7]:


lf_patches = bin_submod.make_likelihood_function(
    tree, bins=2, sites_independent=False, digits=2, space=3
)
lf_patches.set_param_rule("bprobs", is_constant=True)
lf_patches.set_alignment(aln)
lf_patches.optimise(local=True, show_progress=False)
lnL_patches = lf_patches.get_log_likelihood()
df_patches = lf_patches.get_num_free_params()
lf_patches


# In[8]:


LR = lambda alt, null: 2 * (alt - null)


# In[9]:


lr = LR(lnL_bins, lnL_one)
lr


# In[10]:


print("%.4f" % chisqprob(lr, df_patches - df_bins))


# In[11]:


bprobs = lf_patches.get_param_value("bprobs")
print("%.1f : %.1f" % tuple(bprobs))


# In[12]:


pp = lf_patches.get_bin_probs()


# In[13]:


print(pp["bin0"][20])


# In[14]:


from numpy import array

single_kappa = lf_one.get_param_value("kappa")


# In[15]:


kappa_bin_submod = TimeReversibleNucleotide(predicates=[kappa], **treat_gap)
lf_kappa = kappa_bin_submod.make_likelihood_function(
    tree, bins=["slow", "fast"], sites_independent=False, digits=1, space=3
)


# In[16]:


epsilon = 1e-6
lf_kappa.set_param_rule(
    kappa, init=single_kappa - epsilon, upper=single_kappa, bin="slow"
)
lf_kappa.set_param_rule(
    kappa, init=single_kappa + epsilon, lower=single_kappa, bin="fast"
)


# In[17]:


lf_kappa.set_param_rule("bprobs", init=array([1.0 - epsilon, 0.0 + epsilon]))
lf_kappa.set_alignment(aln)
lf_kappa.optimise(local=True, show_progress=False)
lf_kappa

