#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.evolve.models import get_model


# In[3]:


tf = get_model("GY94")
nf = get_model("MG94GTR")
cnf = get_model("CNFGTR")


# In[4]:


from cogent3 import load_aligned_seqs, load_tree

aln = load_aligned_seqs("data/primate_brca1.fasta", moltype="dna")
tree = load_tree("data/primate_brca1.tree")


# In[5]:


lf = cnf.make_likelihood_function(tree, digits=2, space=3)
lf.set_param_rule("omega", is_constant=True, value=1.0)


# In[6]:


optimiser_args = dict(
    local=True, max_restarts=5, tolerance=1e-8, show_progress=False
)
lf.set_alignment(aln)
lf.optimise(**optimiser_args)
lf


# In[7]:


neutral_lnL = lf.get_log_likelihood()
neutral_nfp = lf.get_num_free_params()
lf.set_param_rule("omega", is_constant=False)
lf.optimise(**optimiser_args)
non_neutral_lnL = lf.get_log_likelihood()
non_neutral_nfp = lf.get_num_free_params()
lf


# In[8]:


from cogent3.maths.stats import chisqprob

LR = 2 * (non_neutral_lnL - neutral_lnL)
df = non_neutral_nfp - neutral_nfp
print(chisqprob(LR, df))


# In[9]:


lf.set_param_rule(
    "omega", tip_names=["Chimpanzee", "Human"], outgroup_name="Galago", clade=True
)
lf.optimise(**optimiser_args)
lf
chimp_human_clade_lnL = lf.get_log_likelihood()
chimp_human_clade_nfp = lf.get_num_free_params()


# In[10]:


LR = 2 * (chimp_human_clade_lnL - non_neutral_lnL)
df = chimp_human_clade_nfp - non_neutral_nfp
print(chisqprob(LR, df))


# In[11]:


lf = cnf.make_likelihood_function(tree, digits=2, space=3)
lf.set_alignment(aln)
lf.optimise(**optimiser_args)
non_neutral_lnL = lf.get_log_likelihood()
non_neutral_nfp = lf.get_num_free_params()


# In[12]:


annot_tree = lf.get_annotated_tree()
omega_mle = lf.get_param_value("omega")


# In[13]:


rate_lf = cnf.make_likelihood_function(
    annot_tree, bins=["neutral", "adaptive"], digits=2, space=3
)


# In[14]:


epsilon = 1e-6


# In[15]:


rate_lf.set_param_rule("omega", bin="neutral", upper=1, init=omega_mle)
rate_lf.set_param_rule(
    "omega", bin="adaptive", lower=1 + epsilon, upper=100, init=1 + 2 * epsilon
)


# In[16]:


rate_lf.set_param_rule("bprobs", init=[1 - epsilon, epsilon])


# In[17]:


rate_lf.set_alignment(aln)
rate_lf.optimise(**optimiser_args)
rate_lnL = rate_lf.get_log_likelihood()
rate_nfp = rate_lf.get_num_free_params()
LR = 2 * (rate_lnL - non_neutral_lnL)
df = rate_nfp - non_neutral_nfp
rate_lf


# In[18]:


print(chisqprob(LR, df))


# In[19]:


pp = rate_lf.get_bin_probs()


# In[20]:


from numpy import array
from cogent3 import make_table
from IPython.core.display import HTML

header = ['Site Class', 'Proportion', 'Background Edges', 'Foreground Edges']
data = {'Site Class': array(['0', '1', '2a', '2b'], dtype='<U2'), 'Proportion': array(['p0', 'p1', 'p2', 'p3'], dtype='<U2'), 'Background Edges': array(['0 < omega0 < 1', 'omega1 = 1', '0 < omega0 < 1', 'omega1 = 1'],
  dtype='<U14'), 'Foreground Edges': array(['0 < omega0 < 1', 'omega1 = 1', '0 < omega2 > 1', '0 < omega0 < 1'],
  dtype='<U14')}
data = {k: array(data[k], dtype='U') for k in data}
table = make_table(header, data=data)
HTML(table.set_repr_policy(show_shape=False))


# In[21]:


rate_lf = cnf.make_likelihood_function(tree, bins=["0", "1"], digits=2, space=3)
rate_lf.set_param_rule("omega", bin="0", upper=1.0 - epsilon, init=1 - epsilon)
rate_lf.set_param_rule("omega", bins="1", is_constant=True, value=1.0)
rate_lf.set_alignment(aln)
rate_lf.optimise(**optimiser_args)
tables = rate_lf.get_statistics(with_titles=True)
for table in tables:
    if "bin" in table.title:
        print(table)


# In[22]:


globals = [t for t in tables if "global" in t.title][0]
globals = dict(zip(globals.header, globals.tolist()[0]))
bin_params = [t for t in tables if "bin" in t.title][0]
rate_class_omegas = dict(bin_params.tolist(["bin", "omega"]))
rate_class_probs = dict(bin_params.tolist(["bin", "bprobs"]))
lengths = [t for t in tables if "edge" in t.title][0]
lengths = dict(lengths.tolist(["edge", "length"]))


# In[23]:


rate_branch_lf = cnf.make_likelihood_function(
    tree, bins=["0", "1", "2a", "2b"], digits=2, space=3
)


# In[24]:


for branch, length in lengths.items():
    rate_branch_lf.set_param_rule("length", edge=branch, init=length)


# In[25]:


for param, mle in globals.items():
    rate_branch_lf.set_param_rule(param, init=mle)


# In[26]:


rate_branch_lf.set_param_rule(
    "omega", bins=["0", "2a"], upper=1.0, init=rate_class_omegas["0"]
)
rate_branch_lf.set_param_rule(
    "omega", bins=["1", "2b"], is_constant=True, value=1.0
)
rate_branch_lf.set_param_rule(
    "omega",
    bins=["2a", "2b"],
    edges=["Chimpanzee", "Human"],
    init=99,
    lower=1.0,
    upper=100.0,
    is_constant=False,
)


# In[27]:


rate_branch_lf.set_param_rule(
    "bprobs",
    init=[
        rate_class_probs["0"] - epsilon,
        rate_class_probs["1"] - epsilon,
        epsilon,
        epsilon,
    ],
)


# In[28]:


rate_branch_lf.set_alignment(aln)

