#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import available_models

available_models()


# In[3]:


from cogent3.evolve.models import get_model

hky = get_model("HKY85")
print(hky)


# In[4]:


from cogent3.evolve.models import get_model

sub_mod = get_model("GTR", with_rate=True, distribution="gamma")
print(sub_mod)


# In[5]:


from cogent3.evolve.models import get_model

sub_mod = get_model("CNFGTR", with_rate=True, distribution="gamma")
print(sub_mod)


# In[6]:


from cogent3.evolve.models import get_model

sub_mod = get_model("JTT92", with_rate=True, distribution="gamma")
print(sub_mod)


# In[7]:


from cogent3 import make_tree
from cogent3.evolve.models import get_model

sub_mod = get_model("F81")
tree = make_tree("(a,b,(c,d))")
lf = sub_mod.make_likelihood_function(tree)


# In[8]:


from cogent3 import make_tree, make_aligned_seqs
from cogent3.evolve.models import get_model

sub_mod = get_model("F81")
tree = make_tree("(a,b,(c,d))")
lf = sub_mod.make_likelihood_function(tree)
aln = make_aligned_seqs(
    [("a", "ACGT"), ("b", "AC-T"), ("c", "ACGT"), ("d", "AC-T")]
)
lf.set_alignment(aln)


# In[9]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
print(tree.ascii_art())


# In[10]:


sm = get_model("CNFGTR")
lf = sm.make_likelihood_function(tree, digits=2)
lf.set_param_rule(
    "omega",
    tip_names=["Human", "Orangutan"],
    outgroup_name="Galago",
    clade=True,
    init=0.5,
)


# In[11]:


lf


# In[12]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
sm = get_model("CNFGTR")
lf = sm.make_likelihood_function(tree, digits=2)
lf.set_param_rule("omega", is_constant=True)


# In[13]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
sm = get_model("CNFGTR")
lf = sm.make_likelihood_function(tree, digits=2)
lf.set_param_rule("omega", init=0.1)


# In[14]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
sm = get_model("CNFGTR")
lf = sm.make_likelihood_function(tree, digits=2)
lf.set_param_rule("omega", init=0.1, lower=1e-9, upper=20.0)


# In[15]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
sm = get_model("F81")
lf = sm.make_likelihood_function(tree)
lf.set_param_rule("length", upper=1.0)


# In[16]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

sm = get_model("GTR", with_rate=True, distribution="gamma")
tree = load_tree("data/primate_brca1.tree")
lf = sm.make_likelihood_function(tree, bins=4, digits=2)
lf.set_param_rule("bprobs", is_constant=True)


# In[17]:


from cogent3 import load_tree
from cogent3.evolve.models import get_model

sm = get_model("GTR", with_rate=True, distribution="gamma")
tree = load_tree("data/primate_brca1.tree")
lf = sm.make_likelihood_function(tree, bins=4, sites_independent=False, digits=2)
lf.set_param_rule("bprobs", is_constant=True)


# In[18]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")
sm = get_model("F81")
lf = sm.make_likelihood_function(tree, digits=3, space=2)
lf.set_alignment(aln)
lf.optimise(show_progress=False)


# In[19]:


lf.optimise(local=True, max_restarts=5, show_progress=False)


# In[20]:


lf.optimise(local=False, global_tolerance=1.0, show_progress=False)


# In[21]:


lf.optimise(show_progress=False, max_restarts=5, tolerance=1e-8)


# In[22]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")
sm = get_model("F81")
lf = sm.make_likelihood_function(tree, digits=3, space=2)
lf.set_alignment(aln)
try:
    lf.optimise(
        show_progress=False,
        limit_action="raise",
        max_evaluations=10,
        return_calculator=True,
    )
except ArithmeticError as err:
    print(err)


# In[23]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

sm = get_model("GTR")
tree = load_tree("data/primate_brca1.tree")
lf = sm.make_likelihood_function(tree)
aln = load_aligned_seqs("data/primate_brca1.fasta")
lf.set_alignment(aln)
lf.optimise(local=True, show_progress=False)
lf


# In[24]:


lnL = lf.lnL
lnL


# In[25]:


nfp = lf.nfp
nfp


# In[26]:


lf.get_aic()


# In[27]:


lf.get_aic(second_order=True)


# In[28]:


lf.get_bic()


# In[29]:


a_g = lf.get_param_value("A/G")
a_g


# In[30]:


human = lf.get_param_value("length", "Human")
human


# In[31]:


mprobs = lf.get_motif_probs()
mprobs


# In[32]:


tables = lf.get_statistics(with_motif_probs=True, with_titles=True)
tables[0]  # just displaying the first


# In[33]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")
sm = get_model("F81")
lf = sm.make_likelihood_function(tree, digits=3, space=2)
lf.set_alignment(aln)
lf.set_param_rule(
    "length",
    tip_names=["Human", "Chimpanzee"],
    outgroup_name="Galago",
    clade=True,
    is_independent=False,
)
lf.set_name("Null Hypothesis")
lf.optimise(local=True, show_progress=False)
null_lnL = lf.lnL
null_nfp = lf.nfp
lf


# In[34]:


lf.set_param_rule("length", is_independent=True)
lf.set_name("Alt Hypothesis")
lf.optimise(local=True, show_progress=False)
alt_lnL = lf.lnL
alt_nfp = lf.nfp
lf


# In[35]:


from cogent3.maths.stats import chisqprob

LR = 2 * (alt_lnL - null_lnL)  # the likelihood ratio statistic
df = alt_nfp - null_nfp  # the test degrees of freedom
p = chisqprob(LR, df)
print(f"LR={LR:.4f} ; df={df}; p={df:.4f}")


# In[36]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")

sm = get_model("F81")
lf = sm.make_likelihood_function(tree, digits=3, space=2)
lf.set_alignment(aln)
lf.set_param_rule(
    "length",
    tip_names=["Human", "Chimpanzee"],
    outgroup_name="Galago",
    clade=True,
    is_independent=False,
)
lf.set_name("Null Hypothesis")
lf.optimise(local=True, show_progress=False)
sim_aln = lf.simulate_alignment()
sim_aln[:60]


# In[37]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")
sm = get_model("HKY85")
lf = sm.make_likelihood_function(tree)
lf.set_alignment(aln)
lf.optimise(local=True, show_progress=False)
kappa_lo, kappa_mle, kappa_hi = lf.get_param_interval("kappa")
print(f"lo={kappa_lo:.2f} ; mle={kappa_mle:.2f} ; hi={kappa_hi:.2f}")
human_lo, human_mle, human_hi = lf.get_param_interval("length", "Human")
print(f"lo={human_lo:.2f} ; mle={human_mle:.2f} ; hi={human_hi:.2f}")


# In[38]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

aln = make_aligned_seqs(data=dict(a="ACGG", b="ATAG", c="ATGG"))
tree = make_tree(tip_names=aln.names)
sm = get_model("F81")
lf = sm.make_likelihood_function(tree)
lf.set_alignment(aln)
json = lf.to_json()
json[:60]  # just truncating the displayed string


# In[39]:


from cogent3.util.deserialise import deserialise_object

newlf = deserialise_object(json)
newlf


# In[40]:


from cogent3 import load_tree, load_aligned_seqs
from cogent3.evolve.models import get_model

tree = load_tree("data/primate_brca1.tree")
aln = load_aligned_seqs("data/primate_brca1.fasta")
sm = get_model("F81")
lf = sm.make_likelihood_function(tree, digits=3, space=2)
lf.set_alignment(aln)
lf.optimise(show_progress=False)


# In[41]:


ancestors = lf.likely_ancestral_seqs()
ancestors[:60]


# In[42]:


ancestral_probs = lf.reconstruct_ancestral_seqs()
ancestral_probs["root"][:5]

