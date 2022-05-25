import numpy as np
import pickle
from dl2050utils.df import df_add_datepart


def scaller_norm(s, _mean, _std): return (s-_mean)/_std if _std>0 else s

def scaller_minmax(s, _min, _max): return ((s-_min)/(_max-_min)-0.5)*2.0 if (_max-_min)>0 else s

def scaller_rank(s):
    raise NotImplementedError


class DataFrameProcessor():
    """
    Procecesses Dataframe:
        Transform dates into dateparts
        Split cat and cont vars
        Transform low cardinality cat vars into dummies
        Include NA cols for cont vars
        Calculates stats and normalizes data with a scaller
        Converts cat vars into int32, cont vars into float32, depvar into float32

        Strores processing state for future application on different dataframes
        Saves and loads state into pickle
    """
    
    def __init__(self, c_cat, c_cont, c_dep, c_date, c_key, c_skip, c_onehot, c2, ncats, nconts, cat_szs, emb_szs,
                    cat_dicts, means, stds, medians, mins, maxs, maxhot):
        self.c_cat, self.c_cont, self.c_dep, self.c_date, self.c_key, self.c_skip = c_cat, c_cont, c_dep, c_date, c_key, c_skip
        self.maxhot, self.c_onehot, self.ncats, self.nconts = maxhot, c_onehot, ncats, nconts
        self.cat_szs, self.emb_szs, self.cat_dicts = cat_szs, emb_szs, cat_dicts,
        self.means, self.stds, self.medians, self.mins, self.maxs = means, stds, medians, mins, maxs
        self.c = self.c_skip + self.c_cat + self.c_onehot + self.c_cont
        if c_key is not None: self.c = [c_key] + self.c
        self.c2 = c2
    
    @classmethod
    def from_df(cls, df, c_cat, c_cont, c_dep, c_date=[], c_key=None, c_skip=[], max_embs=50, maxhot=16, embs={}):
        print(f'DataFrameProcessor: building meta')
        df = df.copy()
        # Change args lists access from reference to value
        c_cat, c_cont, c_date = c_cat[:], c_cont[:], c_date[:]
        # Transform dates in dateparts
        for c in c_date:
            c_num = [f'{c}_Dayofyear', f'{c}_Week', f'{c}_Day']
            c_new = df_add_datepart(df, c, drop=False)
            c_cat += [e for e in c_new if e not in c_num]
            c_cont += c_num
        # Calc cardinality of all cats
        cat_szs = {c: len(df[c].unique()) for c in c_cat}
        # For cats with cardinality <= maxhot, transforms into onehot
        c_onehot = [c for c in c_cat if cat_szs[c] <= maxhot]
        # Exclude onehots from cats
        c_cat = [c for c in c_cat if c not in c_onehot]
        cat_szs = {c: cat_szs[c] for c in c_cat}
        # Define embeddings sizes
        emb_szs = [(cat_szs[c]+1, embs[c] if c in embs else min((cat_szs[c]+1)//2, max_embs)) for c in cat_szs]
        # fast.ai heuristic: min(round(1.6*cat_szs[c]**0.56), max_embs)
        # Build one dict (key->index) for all cats (missing values correspond to zero)
        cat_dicts = {c: {} for c in c_cat+c_onehot}
        for c in c_cat+c_onehot:
            cat_dicts[c] = {e: i+1 for i,e in enumerate(list(np.sort(df[df[c].isna()==False][c].astype(str).unique())))}
        # Calculate number of cats and number of conts including onehots
        ncats = len(c_cat)
        nconts = len(c_cont*2)
        for c in c_onehot:
            nconts += len(df[df[c].isna()==False][c].unique())+1
        # Calculate statistics for all conts
        means = {c: df[c].mean() for c in c_cont}
        stds = {c: df[c].std() for c in c_cont}
        medians = {c: df[c].median() for c in c_cont}
        mins = {c: df[c].min() for c in c_cont}
        maxs = {c: df[c].max() for c in c_cont}
        print(f'Done\n')
        return cls(c_cat, c_cont, c_dep, c_date, c_key, c_skip, c_onehot, [], ncats, nconts, cat_szs, emb_szs,
                    cat_dicts, means, stds, medians, mins, maxs, maxhot)
        
    @classmethod
    def from_meta_file(cls, fname):
        meta = pickle.load(open(fname, 'rb'))
        return cls(meta['c_cat'], meta['c_cont'], meta['c_dep'], meta['c_date'],  meta['c_key'], meta['c_skip'],
                    meta['c_onehot'], meta['c2'], meta['ncats'], meta['nconts'], meta['cat_szs'], meta['emb_szs'], 
                    meta['cat_dicts'], meta['means'], meta['stds'], meta['medians'], meta['mins'], meta['maxs'],
                    meta['maxhot'])

    def __call__(self, df):
        print(f'DataFrameProcessor: processing shape={df.shape}')
        df = df.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        for c in self.c_date: _ = df_add_datepart(df, c, drop=True)
        # df = df[self.c]
        for c in self.c:
            un = len(df[c].unique())
            if un<2: print(f'Warning: column {c} with {un} unique values')
        for c in self.c_cat+self.c_onehot:
            df[c] = df[c].astype(str)
            df[c] = [self.cat_dicts[c][e] if e in self.cat_dicts[c] else 0 for e in df[c]]
        c_dummies = []
        for c in self.c_onehot:
            #if len(self.cat_dicts[c]) <= 2:
            #    c_dummies.append(c)
            #    continue
            for e in self.cat_dicts[c]:
                df[c+'_'+e] = (df[c]==self.cat_dicts[c][e])
                c_dummies.append(c+'_'+e)
            df[c+'_na'] = df[c].isna()
            c_dummies.append(c+'_na')
        c_na = []
        for c in self.c_cont:
            # if sum(df[c].isna())==0: continue
            c_na.append(c+'_na')
            df[c+'_na'] = df[c].isna()
            df[c] = df[c].fillna(self.medians[c])
            df[c] = df[c].replace([np.inf, -np.inf], 0.0)
            df[c] = scaller_norm(df[c], self.means[c], self.stds[c])
        c_cont2 = self.c_cont + c_na + c_dummies
        for c in self.c_cat: df[c] = df[c].astype('int32')
        for c in c_cont2: df[c] = df[c].astype('float32')
        self.c2 = self.c_cat + c_cont2
        df = df[self.c2]
        print(f'Done: ncats={len(self.c_cat)}, nconts={len(c_cont2)} ' +\
              f'(numeric={len(c_cont2)-len(c_dummies)-len(c_na)}, na={len(c_na)}, dummies={len(c_dummies)})\n')
        return df
    
    def save_meta(self, fname):
        df_proc_meta = {
            'c_cat': self.c_cat, 'c_cont': self.c_cont, 'c_dep': self.c_dep,
            'c_date': self.c_date, 'c_key': self.c_key, 'c_skip': self.c_skip, 'c_onehot': self.c_onehot, 'c2': self.c2,
            'ncats': self.ncats, 'nconts': self.nconts, 'cat_szs': self.cat_szs, 'emb_szs': self.emb_szs,
            'cat_dicts': self.cat_dicts, 'means': self.means, 'stds': self.stds, 'medians': self.medians,
            'mins': self.mins, 'maxs': self.maxs, 'maxhot': self.maxhot,  
        }
        pickle.dump(df_proc_meta, open(fname, 'wb'))

    def get_emb_szs(self):
        return sorted(list(zip(self.cat_szs, self.emb_szs)), key = lambda e: -e[1][0])


def df_sample(df, n=1000): return df.sample(n=n).copy()
def df_shufle(df): return df.sample(frac=1)


def df_split(df, p1=0.8, p3=None):
    n = len(df)
    perm = np.random.permutation(n)
    cut1 = int(n*p1)
    if p3 is None:
        return df.iloc[perm[:cut1]].copy(), df.iloc[perm[cut1:]].copy()
    cut2 = int(n*(1.-p3))
    return df.iloc[perm[:cut1]].copy(), df.iloc[perm[cut1:cut2]].copy(),  df.iloc[perm[cut2:]].copy()


def df_split_by_date(df, date1, date2=None, date3=None, c_date='date'):
    if date2 is None:
        return df[df[c_date]<date1].copy(), df[df[c_date]>=date1].copy()
    if date3 is None:
        return df[df[c_date]<date1].copy(), df[(df[c_date]>=date1)&(df[c_date]<date2)].copy(), df[df[c_date]>=date2].copy()
    return df[df[c_date]<date1].copy(), df[(df[c_date]>=date1)&(df[c_date]<date2)].copy(), df[(df[c_date]>=date2)&(df[c_date]<date3)].copy()
