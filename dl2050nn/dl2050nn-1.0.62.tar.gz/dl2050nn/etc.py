import random
import math
import datetime
import numpy as np
import pandas as pd
import torch
from matplotlib import pyplot as plt
import seaborn as sns
from dl2050utils.core import *
from dl2050utils.ju import in_ipynb
from IPython.display import display
T = torch.tensor

def get_logprobs(model, x, cuda=True):
    x = torch.Tensor(x)
    if cuda and torch.cuda.is_available():
        x = x.cuda()
    with torch.no_grad():
        y2 = model(x)
    return y2.detach().cpu().numpy()

def get_probs_from_logprobs(y2):
    return np.exp(np.max(y2, axis=1))
    return np.exp(y2[:,1])

def get_preds_from_logprobs(y2):
    return y2.argmax(axis=1)

def get_probs(model, x):
    y2 = get_logprobs(model, x)
    return get_probs_from_logprobs(y2)

def get_preds(model, x):
    y2 = get_logprobs(model, x)
    return get_preds_from_logprobs(y2)

def get_prob_positive(probs, preds):
    probs2 = np.zeros(len(probs))
    m = np.where(preds==1)
    probs2[m] = probs[m]
    return np.round(probs2,2)

def predict(model, x):
    x = torch.Tensor(x).cuda()
    with torch.no_grad():
        y2 = model(x)
    y2 = y2.detach().cpu().numpy()
    preds = y2.argmax(axis=1)
    return preds

def norm(x):
    m,s = x.mean(), x.std()
    return (x-m)/s if s>0 else x

def frmt_n(n): return f'{n:,}'.replace(',','.')

def show_clsf_stats(y, c, cls, c_szs, c_dist):
    df = pd.concat([
        pd.DataFrame(np.arange(0,len(cls)),columns=['cls']),
        pd.DataFrame(cls,columns=['labels']),
        pd.DataFrame(c_szs,columns=['size']),
        pd.DataFrame(c_dist,columns=['dist'])
    ], axis=1)
    print(f'\nClassification dataset: {frmt_n(len(y))} records, {frmt_n(c)} classes')
    if len(y.shape)>1: print(f'Total number of labels {y.shape} -> {np.asarray(c_szs).sum():,}')
    display(df)

def prep_cls(y, cls_to_idx=None, cls=None):
    assert (type(y)==list or type(y)==np.ndarray)
    
    size,labels,cls2idx,cls2 = 0,None,None,None
    if type(y)==list:
        size = len(y)
        labels = [str(e) for e in y]
        if cls_to_idx is not None:
            cls2idx = cls_to_idx
            cls2 = [e for e in cls2idx]
            for label in labels:
                if label not in cls2:
                    raise Exception(f'Label {label} not found in cls_to_idx')
        else:
            cls2 = sorted(list(set(labels)))
            cls2idx = {cls2[i]: i for i in range(len(cls2))}
        if type(y[0])==str:
            y = [cls2idx[label] for label in labels]
        y = np.asarray(y)
        c_idxs = [(y==cls2idx[c]).nonzero()[0] for c in cls2idx]
    else:
        y1 = y.flatten()
        size = len(y1)
        cls1 = np.unique(y1)
        c_idxs = [(y==cls1[c]).nonzero()[0] for c in cls1]
        cls2 = cls or cls1
    c_szs = [e.shape[0] for e in c_idxs]
    c_dist = [e.shape[0]/size for e in c_idxs]
    return y,cls2,len(cls2),labels,cls2idx,c_idxs,c_szs,c_dist

def np_split(x, y, p=.8):
    idx = np.random.permutation(x.shape[0])
    k = int(x.shape[0]*p)
    x,y = x[idx].copy(),y[idx].copy()
    return x[:k],y[:k],x[k:],y[k:]

def get_sample(x1, y1, x2, y2, sz=1000, sz2=None):
    if sz2 is None: sz2=sz
    p = np.random.permutation(len(x1))
    x1, y1 = x1[p], y1[p]
    p = np.random.permutation(len(x2))
    x2, y2 = x2[p], y2[p]
    return x1[:sz], y1[:sz], x2[:sz2], y2[:sz2]

def plot(x, y):
    plt.figure()
    plt.plot(x,y)
    plt.show()
    plt.pause(.001)

def imgrid(x, y):
    if len(x.shape) not in [3,4]: Exception('x dims must be 3 ou 4')
    if len(x.shape)==3: x = x[None,:,:,:]
    n = x.shape[0]
    nc = 4
    nr = math.ceil(n/nc)
    fig, axs = plt.subplots(nr, nc, figsize=(15,4*nr))
    if type(axs)!=np.ndarray: axs = [[axs]]
    elif len(axs.shape)==1: axs = [axs]
    for i in range(n):
        r,c = i//nc,i%nc
        ax = axs[r][c]
        xi = x[i] if x[i].shape[2]>2 else x[i].squeeze(-1)
        ax.imshow(xi)
        ax.set_title(y[i])
    fig.tight_layout()
    plt.show()
    plt.pause(0.01)

def plot_signal(x, ch=0, title=None):
    plt.plot(x[ch])
    if title: plt.title(title)
    plt.show()
    plt.pause(0.001)
    
def sigshow(x, title):
    n = x.shape[0]
    nc = 2
    nr = math.ceil(n/nc)
    fig, axs = plt.subplots(nr, nc, figsize=(15,2*nr))
    for i in range(n):
        r,c = i//nc,i%nc
        axs[r][c].plot(x[i])
        axs[r][c].set_title(f'Channel {i}')
    fig.tight_layout()
    plt.show()
    plt.pause(0.001)


# def np_split(x, y, p=.2):
#     mask = np.random.permutation(len(x))
#     k = int(len(x)*(1-p))
#     x1, y1 = x[mask[:k]], y[mask[:k]]
#     x2, y2 = x[mask[k:]], y[mask[k:]]
#     return x1, y1, x2, y2


# def get_sample(x1, y1, x2, y2, sz=1000):
#     p = np.random.permutation(len(x1))
#     x1, y1 = x1[p], y1[p]
#     p = np.random.permutation(len(x2))
#     x2, y2 = x2[p], y2[p]
#     return x1[:sz], y1[:sz], x2[:sz], y2[:sz]
# x1, y1, x2, y2 = get_sample(x1, y1, x2, y2)
# x1.shape, y1.shape, x2.shape, y2.shape


# torch.Tensor.ndim = property(lambda x: len(x.shape))
def _tuple(x): return x if isinstance(x, (list, tuple)) else (x,x)
NoneType = type(None)
def noop (x=None, *args, **kwargs): return x
def t2s(t): return f'{int(t)//60:02d}:{int(t)%60:02d}'


def get_date_str(): 
    d = datetime.datetime.now()
    return  f'{d.year:04d}{d.month:02d}{d.day:02d}-{d.hour:02d}{d.minute:02d}{d.second:02d}'


def get_log_fname(path):
    dirname = path/'runs'
    fname = f'{dirname}/run-{get_date_str()}.csv'
    return fname, dirname


def save_model(model, path, stats):
    state = {'state_dict': model.state_dict(), 'stats': stats}
    torch.save(state, path)

def load_model(model, path, cuda=False, inference=False, show=False):
    state = torch.load(path, map_location='cpu')
    model.load_state_dict(state['state_dict'])
    stats = state['stats']
    if show:
        pd.options.display.float_format = '{:,.4f}'.format
        display(pd.DataFrame.from_dict(stats))
    if cuda and torch.cuda.is_available():
        model.cuda()
    if inference:
        model.eval()
    return stats


def get_model_n_params(model):
    return sum([p.numel() for p in model.parameters()])

def xy_shuffle_split(x, y, p=0.2):
    msk = np.random.permutation(len(x))
    n = int(len(x)*p)
    return x[msk[:n]], y[msk[:n]], x[msk[n:]], y[msk[n:]]


def get_cls_dist(y, cls_to_idx):
    if type(y)==list: y = np.array([cls_to_idx[e] for e in y])
    elif type(y)==torch.Tensor: y = y.numpy()
    c_idxs = [np.asarray(y==cls_to_idx[c]).nonzero()[0] for c in cls_to_idx]
    c_szs = [e.shape[0] for e in c_idxs]
    c_dist = [e.shape[0]/len(y) for e in c_idxs]
    return c_idxs, c_szs, c_dist


def get_cls_dist_string(cls, c_szs, c_dist):
    return ', '.join([f'({c} {s} {d:.2f})' for c,s,d in sorted(zip(cls, c_szs, c_dist), key = lambda t: -t[1])])


def get_cnn_szs(net, sz):
    if sz is None: return []
    C0, H0, W0 = sz
    C1, H1, W1 = C0, H0, W0
    szs = [(C0, H0, W0)]
    for name, l in net.named_modules():
        classname = l.__class__.__name__
        if classname == 'Conv2d':
            stride = _tuple(l.stride)
            padding = _tuple(l.padding)
            kernel_size = _tuple(l.kernel_size)
            dilation = _tuple(l.dilation)
            C1 = int(l.out_channels)
            H1 = int(math.floor((H0 + 2 * padding[0] - dilation[0] * (kernel_size[0] - 1) - 1) / stride[0] + 1))
            W1 = int(math.floor((W0 + 2 * padding[1] - dilation[1] * (kernel_size[1] - 1) - 1) / stride[1] + 1))
            szs.append([(C1, H1, W1)])
        C0, H0, W0 = C1, H1, W1
    return szs


def biased_roll(dist):
    r = random.random()
    cum, result = 0, 0
    for d in dist:
        cum += d
        if r < cum: return result
        result += 1


def table(cols, vals):
    pd.options.display.float_format = '{:,.4f}'.format
    display(pd.DataFrame(vals, columns=cols))


# Deprecated
# def show_dist(y):
#     df = pd.DataFrame(y, columns=['count'])['count'].value_counts()
#     df = pd.DataFrame(df, index=df.index, columns=['count'])
#     df['p'] = df['count']/sum(df['count'])
#     display(df)
    # print(get_cls_dist_string(self.cls, self.c_szs, self.c_dist))


# def calc_norm(self):
#     xs, ys = [], []
#     for i in range(len(self)):
#         x, y = self[i]
#         xs.append(x)
#         ys.append(y)
#     x, y = torch.stack(xs, 0), torch.stack(ys, 0)
#     mean = [x[:,i,:,:].mean().item() for i in range(3)]
#     std = [x[:,i,:,:].std().item() for i in range(3)]
#     return mean, std



# # L()

# def is_iter(o):
#     "Test whether `o` can be used in a `for` loop"
#     #Rank 0 tensors in PyTorch are not really iterable
#     return isinstance(o, (Iterable,Generator)) and getattr(o,'ndim',1)


# def mask2idxs(mask):
#     "Convert bool mask or index list to index `L`"
#     if isinstance(mask,slice): return mask
#     mask = list(mask)
#     if len(mask)==0: return []
#     it = mask[0]
#     if hasattr(it,'item'): it = it.item()
#     if isinstance(it,(bool,NoneType,np.bool_)): return [i for i,m in enumerate(mask) if m]
#     #if isinstance(it,(bool,np.bool_)): return [i for i,m in enumerate(mask) if m]
#     return [int(i) for i in mask]


# def _is_array(x): return hasattr(x,'__array__') or hasattr(x,'iloc')


# def is_indexer(idx):
#     "Test whether `idx` will index a single item in a list"
#     return isinstance(idx,int) or not getattr(idx,'ndim',1)


# def _listify(o):
#     if o is None: return []
#     if isinstance(o, list): return o
#     if isinstance(o, str) or _is_array(o): return [o]
#     if is_iter(o): return list(o)
#     return [o]


# def coll_repr(c, max_n=10):
#     "String repr of up to `max_n` items of (possibly lazy) collection `c`"
#     return f'(#{len(c)}) [' + ','.join(itertools.islice(map(str,c), max_n)) + (
#         '...' if len(c)>10 else '') + ']'


# class CollBase:
#     "Base class for composing a list of `items`"
#     def __init__(self, items): self.items = items
#     def __len__(self): return len(self.items)
#     def __getitem__(self, k): return self.items[k]
#     def __setitem__(self, k, v): self.items[list(k) if isinstance(k,CollBase) else k] = v
#     def __delitem__(self, i): del(self.items[i])
#     def __repr__(self): return self.items.__repr__()
#     def __iter__(self): return self.items.__iter__()


# class L(CollBase):
#     "Behaves like a list of `items` but can also index with list of indices or masks"
#     _default='items'
#     def __init__(self, items=None, *rest, use_list=False, match=None):
#         if rest: items = (items,)+rest
#         if items is None: items = []
#         if (use_list is not None) or not _is_array(items):
#             items = list(items) if use_list else _listify(items)
#         if match is not None:
#             if is_coll(match): match = len(match)
#             if len(items)==1: items = items*match
#             else: assert len(items)==match, 'Match length mismatch'
#         super().__init__(items)

#     @property
#     def _xtra(self): return None
#     def _new(self, items, *args, **kwargs): return type(self)(items, *args, use_list=None, **kwargs)
#     def __getitem__(self, idx): return self._get(idx) if is_indexer(idx) else L(self._get(idx), use_list=None)
#     def copy(self): return self._new(self.items.copy())

#     def _get(self, i):
#         if is_indexer(i) or isinstance(i,slice): return getattr(self.items,'iloc',self.items)[i]
#         i = mask2idxs(i)
#         return (self.items.iloc[list(i)] if hasattr(self.items,'iloc')
#                 else self.items.__array__()[(i,)] if hasattr(self.items,'__array__')
#                 else [self.items[i_] for i_ in i])

#     def __setitem__(self, idx, o):
#         "Set `idx` (can be list of indices, or mask, or int) items to `o` (which is broadcast if not iterable)"
#         idx = idx if isinstance(idx,L) else _listify(idx)
#         if not is_iter(o): o = [o]*len(idx)
#         for i,o_ in zip(idx,o): self.items[i] = o_

#     def __iter__(self): return iter(self.items.itertuples() if hasattr(self.items,'iloc') else self.items)
#     def __contains__(self,b): return b in self.items
#     def __invert__(self): return self._new(not i for i in self)
#     def __eq__(self,b): return False if isinstance(b, (str,dict,set)) else all_equal(b,self)
#     def __repr__(self): return repr(self.items) if _is_array(self.items) else coll_repr(self)
#     def __mul__ (a,b): return a._new(a.items*b)
#     def __add__ (a,b): return a._new(a.items+_listify(b))
#     def __radd__(a,b): return a._new(b)+a
#     def __addi__(a,b):
#         a.items += list(b)
#         return a

#     def sorted(self, key=None, reverse=False):
#         if isinstance(key,str):   k=lambda o:getattr(o,key,0)
#         elif isinstance(key,int): k=itemgetter(key)
#         else: k=key
#         return self._new(sorted(self.items, key=k, reverse=reverse))

#     @classmethod
#     def split(cls, s, sep=None, maxsplit=-1): return cls(s.split(sep,maxsplit))

#     @classmethod
#     def range(cls, a, b=None, step=None):
#         if is_coll(a): a = len(a)
#         return cls(range(a,b,step) if step is not None else range(a,b) if b is not None else range(a))

#     def map(self, f, *args, **kwargs):
#         g = (bind(f,*args,**kwargs) if callable(f)
#              else f.format if isinstance(f,str)
#              else f.__getitem__)
#         return self._new(map(g, self))

#     def filter(self, f, negate=False, **kwargs):
#         if kwargs: f = partial(f,**kwargs)
#         if negate: f = negate_func(f)
#         return self._new(filter(f, self))

#     def unique(self): return L(dict.fromkeys(self).keys())
#     def enumerate(self): return L(enumerate(self))
#     def val2idx(self): return {v:k for k,v in self.enumerate()}
#     def itemgot(self, *idxs):
#         x = self
#         for idx in idxs: x = x.map(itemgetter(idx))
#         return x
    
#     def attrgot(self, k, default=None): return self.map(lambda o:getattr(o,k,default))
#     def cycle(self): return cycle(self)
#     def map_dict(self, f=noop, *args, **kwargs): return {k:f(k, *args,**kwargs) for k in self}
#     def starmap(self, f, *args, **kwargs): return self._new(itertools.starmap(partial(f,*args,**kwargs), self))
#     def zip(self, cycled=False): return self._new((zip_cycle if cycled else zip)(*self))
#     def zipwith(self, *rest, cycled=False): return self._new([self, *rest]).zip(cycled=cycled)
#     def map_zip(self, f, *args, cycled=False, **kwargs): return self.zip(cycled=cycled).starmap(f, *args, **kwargs)
#     def map_zipwith(self, f, *rest, cycled=False, **kwargs): return self.zipwith(*rest, cycled=cycled).starmap(f, **kwargs)
#     def concat(self): return self._new(itertools.chain.from_iterable(self.map(L)))
#     def shuffle(self):
#         it = copy(self.items)
#         random.shuffle(it)
#         return self._new(it)
    
#     def append(self,o): return self.items.append(o)
#     def remove(self,o): return self.items.remove(o)
#     def count (self,o): return self.items.count(o)
#     def reverse(self ): return self.items.reverse()
#     def pop(self,o=-1): return self.items.pop(o)
#     def clear(self   ): return self.items.clear()
#     def index(self, value, start=0, stop=sys.maxsize): return self.items.index(value, start=start, stop=stop)
#     def sort(self, key=None, reverse=False): return self.items.sort(key=key, reverse=reverse)
