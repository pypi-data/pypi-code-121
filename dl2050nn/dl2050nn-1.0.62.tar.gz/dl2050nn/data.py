import random
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from IPython.display import display
from dl2050utils.core import *
from dl2050utils.fs import get_dir_files, get_dir_dirs
from dl2050nn.etc import *
from dl2050nn.tabular import DataFrameProcessor

# if regr:
#     yrange = [df[c_dep].astype('float32').min(), df[c_dep].astype('float32').max()]

################################################################################################################################
#  DataLoader
#
# TODO: num_workers, pin_memory
################################################################################################################################

def get_balanced_idxs(c_idxs, p=0.):
    p = min(max(p,0.),1.)
    szs = np.array([len(e) for e in c_idxs])
    n = szs.sum()
    bp0 = np.array([len(c)/n for c in c_idxs])
    bp1 = np.array([1/len(c_idxs)]*len(c_idxs))
    bp = bp0+p*(bp1-bp0)
    m = bp/bp0
    szs2 = np.round((szs*m/m.min())).astype(int)
    z = np.array([])
    for i in range(len(c_idxs)):
        for _ in range(szs2[i]//szs[i]): z = np.concatenate((z,np.array(c_idxs[i])))
        z = np.concatenate((z,np.array(c_idxs[i])[:szs2[i]%szs[i]]))
    z = np.random.permutation(z)
    return z.astype(int)

def collate(b):
    x,y = zip(*b)
    return torch.stack(x),torch.stack(y)

class SimpleSampler():
    def __init__(self, ds, bs):
        self.n,self.bs = len(ds),bs
    def set_balance(self, p):
        pass
    def __iter__(self):
        self.idxs = list(range(0,self.n))
        for i in range(0, self.n, self.bs): yield self.idxs[i:i+self.bs]

class RandomSampler():
    def __init__(self, ds, bs, c_idxs):
        self.n,self.bs,self.c_idxs,self.p = len(ds),bs,c_idxs,None
    def set_balance(self, p):
        self.p = p
    def __iter__(self):
        if self.p is None or self.c_idxs is None:
            self.idxs = list(np.random.permutation(np.arange(self.n)))
        else:
            self.idxs = list(get_balanced_idxs(self.c_idxs, p=self.p))
        for i in range(0, self.n, self.bs): yield self.idxs[i:i+self.bs]

class DataLoader():
    def __init__(self, ds, bs=64, shuffle=False, collate_fn=collate):
        self.ds, self.bs, self.collate_fn, self.n = ds, bs, collate_fn, len(ds)
        self.sampler = SimpleSampler(ds, bs) if not shuffle else RandomSampler(ds, bs, self.ds.c_idxs)
    def set_balance(self, p): self.sampler.set_balance(p)
    def __len__(self): return math.ceil(len(self.ds)/self.bs)
    def __iter__(self):
        for b in self.sampler: yield self.collate_fn([self.ds[i] for i in b])

################################################################################################################################
# Dataset, Data
#
# Classification: y type is list or numpy long
# Mask of integers: 2D classification
# Mask of floats: ???
# Regression: y type is float scalar
#
################################################################################################################################

class Dataset():
    def __init__(self, x, y, aug_size=None, clsf=False, cls_to_idx=None, cls=None, regr=False, trfs=[]):
        self.x,self.y,self.aug_size,self.clsf,self.regr,self.trfs = x,y,aug_size,clsf,regr,trfs or []
        self.bps,self.c_idxs = None,None
        if clsf:
            y,self.cls,self.c,self.labels,self.cls_to_idx,self.c_idxs,self.c_szs,self.c_dist = prep_cls(y, cls_to_idx=cls_to_idx, cls=cls)
            self.y = y.astype(np.int32)
            show_clsf_stats(self.y, self.c, self.cls, self.c_szs, self.c_dist)
        else:
            self.y = y.astype(np.float32)
        self.x = x #.astype(np.float64)
        
    def __len__(self): return self.aug_size or len(self.x)
    def __getitem__(self, i):
        if self.aug_size: i=random.randint(0,len(self.x)-1)
        x,y = self.load(self.x[i], self.y[i])
        for trf in self.trfs: x,y=trf(x,y)
        x = torch.from_numpy(x).float()
        y = torch.from_numpy(y) if len(y.shape)>0 else torch.tensor(y).float()
        if self.clsf: y = y.long()
        return x,y
    def load(self, x, y): return x,y
    def show(self, idxs, labels=None):
        for idx in listify(idxs):
            x,y = self[idx]
            print(x.shape, y.shape)
    def show_trfs(self, n=8): self.show([random.randint(0,len(self))]*n)
    def encode(self, x, y): pass
    def decode(self,x,y): return x.numpy(),y.item()


class Data:
    def __init__(self, ds1, ds2, bs=64):
        self.ds1, self.ds2 =  ds1, ds2
        self.bs = bs
        # w, pin = 0, torch.cuda.is_available()
        self.dl1 = DataLoader(ds1, bs=bs, shuffle=True)
        self.dl2 = DataLoader(ds2, bs=bs, shuffle=False) if ds2 is not None else None

    def show_batch(self, n=8): self.ds1.show(next(iter(self.dl1.sampler))[:n])
    def show_batch_2(self, n=8): self.ds2.show(next(iter(self.dl2.sampler))[:n])
    def show_trfs(self, n=8): self.ds1.show_trfs(n=n)

    @property
    def clsf(self): return self.ds1.clsf
    @property
    def regr(self): return self.ds1.regr
    @property
    def c(self): return self.ds1.c if self.clsf else None
    @property
    def cls(self): return self.ds1.cls if self.clsf else None
    @property
    def cls_to_idx(self): return self.ds1.cls_to_idx if self.clsf else None

    @classmethod
    def from_numpy(cls, x1, y1, x2, y2, aug_size1=None, aug_size2=None, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64):
        ds1 = Dataset(x1, y1,aug_size=aug_size1, clsf=clsf, regr=regr, trfs=trfs1)
        ds2 = Dataset(x2, y2, aug_size=aug_size2, clsf=clsf, regr=regr, trfs=trfs2)
        return cls(ds1, ds2, bs=bs)

################################################################################################################################
#  SignalDataset, SignalData
################################################################################################################################

class SignalDataset(Dataset):    
    def __init__(self, *args, **kwargs):
        super(SignalDataset, self).__init__(*args, **kwargs)
    def show(self, idxs, labels=None):
        idxs, labels = listify(idxs), listify(labels)
        for i,idx in enumerate(idxs):
            x,y = self.decode(*self[idx])
            if self.clsf: y = self.cls[y]
            label = labels[i] if len(labels) else y
            sigshow(x, label or y)

class SignalData(Data):
    def __init__(self, x1, y1, x2, y2, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64):
        ds1 = SignalDataset(x1, y1, clsf=clsf, regr=regr, trfs=trfs1)
        ds2 = SignalDataset(x2, y2, clsf=clsf, regr=regr, trfs=trfs2)
        super(SignalData, self).__init__(ds1, ds2, bs=bs)
        
    @classmethod
    def from_numpy(cls, x1, y1, x2, y2, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64):
        # x1,x2 = torch.from_numpy(x1).float(),torch.from_numpy(x2).float()
        # if clsf: y1, y2 = list(y1), list(y2)
        # else: y1, y2 = torch.from_numpy(y1).float(), torch.from_numpy(y2).float()
        return cls(x1, y1, x2, y2, clsf=clsf, regr=regr, trfs1=trfs1, trfs2=trfs2, bs=bs)

################################################################################################################################
#  ImageDataset, ImageDatasetMem, ImageData
################################################################################################################################

class ImageDataset(Dataset):    
    def load(self,x,y): return Image.open(x),y
    def decode(self, x, y): return transforms.ToPILImage()(x),y
    def show(self, idxs, labels=None):
        idxs, labels = listify(idxs), listify(labels)
        x,y = zip(*[self.decode(*self[idx]) for idx in idxs])
        x = np.stack([np.array(x) for x in x])
        if self.clsf: y = [self.cls[e] for e in y]
        imgrid(x, labels or y)


class ImageDatasetMem(ImageDataset):
    def load(self,x,y): return x,y
    def decode(self,x,y): return x.numpy().transpose((1,2,0)),y


class ImageData(Data):
    def __init__(self, x1, y1, x2, y2, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64, ds_class=ImageDataset):
        ds1 = ds_class(x1, y1, clsf=clsf, regr=regr, trfs=trfs1)
        ds2 = ds_class(x2, y2, clsf=clsf, regr=regr, trfs=trfs2, cls_to_idx=ds1.cls_to_idx)
        super(ImageData, self).__init__(ds1, ds2, clsf=clsf, regr=regr, bs=bs)
        
    @classmethod
    def from_folder(cls, path1, path2, types=None, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64):
        x, y = [[],[]], [[],[]]
        cls_names = [d.stem for d in get_dir_dirs(path1)]
        for i,path in enumerate([path1, path2]):
            for c in cls_names:
                for f in get_dir_files(path/f'{c}', types):
                    x[i].append(f)
                    y[i].append(c)
        return cls(x[0], y[0], x[1], y[1], clsf=clsf, regr=regr, trfs1=trfs1, trfs2=trfs2, bs=bs)

    @classmethod
    def from_numpy(cls, x1, y1, x2, y2, clsf=False, regr=False, trfs1=[], trfs2=[], bs=64):
        x1, y1, x2, y2 = T(x1).float(), y1, T(x2).float(), y2
        return cls(x1, y1, x2, y2, clsf=clsf, regr=regr, trfs1=trfs1, trfs2=trfs2, bs=bs, ds_class=ImageDatasetMem)

################################################################################################################################
#   TabularDataset, TabularData
################################################################################################################################

class TabularDataset(Dataset):
    def __init__(self, df, dfp, proc, clsf=False, cls_to_idx=None, regr=False):
        self.df, self.dfp = df, dfp
        x  = dfp[proc.c2].values
        x = torch.from_numpy(x).float()
        y = [str(e) for e in df[proc.c_dep].values]
        super(TabularDataset, self).__init__(x, y, clsf=clsf, cls_to_idx=cls_to_idx, regr=regr)
        if len(proc.get_emb_szs()): print(f'Embeddings: {proc.get_emb_szs()}')

    def show(self, idxs, labels=None, cols=None):
        df = self.df.iloc[listify(idxs)][cols or self.df.columns]
        df['results'] = labels
        display(df)


class TabularData(Data):
    def __init__(self, df1, df1p, df2, df2p, proc, clsf=False, regr=False, bs=128):
        self.df1, self.df1p, self.df2, self.df2p, self.proc = df1, df1p, df2, df2p, proc
        ds1 = TabularDataset(df1, df1p, proc, clsf=clsf, regr=regr)
        ds2 = TabularDataset(df2, df2p, proc, clsf=clsf, regr=regr,  cls_to_idx=ds1.cls_to_idx) if df2p is not None else None
        super(TabularData, self).__init__(ds1, ds2, clsf=clsf, regr=regr, bs=bs)

    @classmethod
    def from_dfs(cls, df1, df2, c_cat, c_cont, c_dep, c_date=[], c_key=None, c_skip=[], maxhot=16, max_embs=4, embs={}, path='.', 
                    clsf=False, regr=False, name='tabular', bs=256):
        proc = DataFrameProcessor.from_df(df1, c_cat, c_cont, c_dep, c_date=c_date, c_key=c_key, c_skip=c_skip, maxhot=maxhot,
                                            max_embs=max_embs, embs=embs)
        df1p = proc(df1)
        proc.save_meta(f'{path}/{name}_proc.pickle')
        df1.reset_index(drop=True).to_feather(f'{path}/{name}_df1.feather')
        df1p.reset_index(drop=True).to_feather(f'{path}/{name}_df1p.feather')
        df2p = None
        if df2 is not None:
            df2p = proc(df2)
            df2.reset_index(drop=True).to_feather(f'{path}/{name}_df2.feather')
            df2p.reset_index(drop=True).to_feather(f'{path}/{name}_df2p.feather')
        return cls(df1, df1p, df2, df2p, proc, clsf=clsf, regr=regr, bs=bs)

    @classmethod
    def from_feather(cls, path='.', name='tabular', clsf=False, regr=False, bs=128, valid=True):
        proc = DataFrameProcessor.from_meta_file(f'{path}/{name}_proc.pickle')
        df1 = feather.read_dataframe(f'{path}/{name}_df1.feather')
        df1p = feather.read_dataframe(f'{path}/{name}_df1p.feather')
        if not valid: return cls(df1, df1p, None, None, proc, clsf=clsf, regr=regr, bs=bs)
        df2, df2p = None, None
        if Path(f'{path}/{name}_df2.feather').is_file():
            df2 = feather.read_dataframe(f'{path}/{name}_df2.feather')
            df2p = feather.read_dataframe(f'{path}/{name}_df2p.feather')
        return cls(df1, df1p, df2, df2p, proc, clsf=clsf, regr=regr, bs=bs)

    def encode(self, df): return torch.from_numpy(self.proc(df)[self.proc.c2].values).float()
    def decode(self): pass

    @property
    def ncats(self): return self.proc.ncats
    @property
    def nconts(self): return self.proc.nconts
    @property
    def maxhot(self): return self.proc.maxhot
    @property
    def cat_szs(self): return self.proc.cat_szs
    @property
    def emb_szs(self): return self.proc.emb_szs
