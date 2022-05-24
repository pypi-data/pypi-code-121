#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


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


# In[3]:


from cogent3.app import io, evo

loader = io.load_aligned(format="fasta", moltype="dna")
aln = loader("data/primate_brca1.fasta")

zhang_test = evo.natsel_zhang(
    "GNC",
    tree="data/primate_brca1.tree",
    optimise_motif_probs=False,
    tip1="Human",
    tip2="Chimpanzee",
)

result = zhang_test(aln)
result


# In[4]:


result.alt.lf


# In[5]:


bprobs = result.alt.lf.get_bin_probs()
bprobs[:, :20]


# In[6]:


tab = evo.tabulate_stats()
stats = tab(result.alt)
stats


# In[7]:


stats["edge bin params"][:10]  # truncating the table

