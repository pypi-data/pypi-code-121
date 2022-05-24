#!/usr/bin/env python
# coding: utf-8

# In[1]:


import set_working_directory


# In[2]:


from cogent3.app.io import get_data_store

dstore = get_data_store("data/raw.zip", suffix="fa*", limit=5)
dstore


# In[3]:


m = dstore[0]
m


# In[4]:


m.read()[:20]  # truncating


# In[5]:


dstore.tail()


# In[6]:


dstore.filtered("*ENSG00000067704*")


# In[7]:


for m in dstore:
    print(m)


# In[8]:


dstore = get_data_store("data/demo-locked.tinydb")
dstore.describe


# In[9]:


dstore.unlock(force=True)


# In[10]:


dstore.summary_logs


# In[11]:


dstore.logs


# In[12]:


print(dstore.logs[0].read()[:225])  # truncated for clarity

