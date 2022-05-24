#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy

numpy.random.seed(11)


# In[2]:


import numpy

t = numpy.arange(0, 10, 0.1)
n = numpy.random.randn(len(t))
nse = numpy.convolve(n, numpy.exp(-t / 0.05)) * 0.1
nse = nse[: len(t)]
sig = numpy.sin(2 * numpy.pi * t) + nse


# In[3]:


from cogent3.maths.period import dft

pwr, period = dft(sig)
print(period)
print(pwr)


# In[4]:


pwr = abs(pwr)
max_pwr, max_period = sorted(zip(pwr, period))[-1]
print(max_pwr, max_period)


# In[5]:


from cogent3.maths.period import auto_corr

pwr, period = auto_corr(sig)
print(period)
print(pwr)


# In[6]:


max_pwr, max_period = sorted(zip(pwr, period))[-1]
print(max_pwr, max_period)


# In[7]:


s = (
    "ATCGTTGGGACCGGTTCAAGTTTTGGAACTCGCAAGGGGTGAATGGTCTTCGTCTAACGCTGG"
    "GGAACCCTGAATCGTTGTAACGCTGGGGTCTTTAACCGTTCTAATTTAACGCTGGGGGGTTCT"
    "AATTTTTAACCGCGGAATTGCGTC"
)


# In[8]:


from cogent3.maths.stats.period import SeqToSymbols

seq_to_symbols = SeqToSymbols(["AA", "TT", "AT"])
symbols = seq_to_symbols(s)
len(symbols) == len(s)
symbols


# In[9]:


from cogent3.maths.period import ipdft

powers, periods = ipdft(symbols)
powers


# In[10]:


periods


# In[11]:


from cogent3.maths.period import auto_corr, hybrid

powers, periods = auto_corr(symbols)
powers


# In[12]:


periods


# In[13]:


powers, periods = hybrid(symbols)
powers


# In[14]:


periods


# In[15]:


from cogent3.maths.period import goertzel

pwr = goertzel(sig, 10)
print(pwr)


# In[16]:


powers, periods = auto_corr(symbols)
llim = 2
period5 = 5 - llim
periods[period5]


# In[17]:


powers[period5]


# In[18]:


from cogent3.maths.period import goertzel

period = 4
power = goertzel(symbols, period)
ipdft_powers, periods = ipdft(symbols)
ipdft_power = abs(ipdft_powers[period - llim])
round(power, 6) == round(ipdft_power, 6)
power


# In[19]:


power = hybrid(symbols, period=period)
power


# In[20]:


from cogent3.maths.period import Goertzel

goertzel_calc = Goertzel(len(sig), period=10)


# In[21]:


from cogent3.maths.stats.period import blockwise_bootstrap

obs_stat, p = blockwise_bootstrap(
    sig, calc=goertzel_calc, block_size=10, num_reps=1000
)
print(obs_stat)
print(p)


# In[22]:


from cogent3.maths.period import Hybrid

hybrid_calculator = Hybrid(len(s), period=4)


# In[23]:


from cogent3.maths.stats.period import SeqToSymbols

seq_to_symbols = SeqToSymbols(["AA", "TT", "AT"], length=len(s))


# In[24]:


from cogent3.maths.stats.period import blockwise_bootstrap

stat, p = blockwise_bootstrap(
    s,
    calc=hybrid_calculator,
    block_size=10,
    num_reps=1000,
    seq_to_symbols=seq_to_symbols,
)
print(stat)
p < 0.1

