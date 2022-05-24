#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3 import load_aligned_seqs, make_tree
from cogent3.evolve.substitution_model import EmpiricalProteinMatrix
from cogent3.parse.paml_matrix import PamlMatrixParser


# In[3]:


treestring = "(((rabbit,rat),human),goat-cow,marsupial);"
t = make_tree(treestring)


# In[4]:


al = load_aligned_seqs("data/abglobin_aa.phylip", moltype="protein")


# In[5]:


matrix_file = open("data/dayhoff.dat")


# In[6]:


empirical_matrix, empirical_frequencies = PamlMatrixParser(matrix_file)


# In[7]:


sm = EmpiricalProteinMatrix(empirical_matrix, empirical_frequencies)


# In[8]:


lf = sm.make_likelihood_function(t)
lf.set_alignment(al)
lf.optimise(show_progress=False)
lf

