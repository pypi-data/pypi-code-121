import pandas as pd
import sparse
from scipy.sparse import coo_matrix
from pandas.api.types import CategoricalDtype


class SparseLodes:
    def __int__(self, df):
        geocodes = pd.unique(df[['w_geocode', 'h_geocode']].values.ravel('K'))
        jobs = [c for c in df.columns if c not in ['w_geocode', 'h_geocode']]
        shape = (len(geocodes), len(geocodes))

        # Map geocodes to coded index
        self.jobs_cat = CategoricalDtype(categories=sorted(jobs), ordered=True)
        self.geocodes_cat = CategoricalDtype(categories=sorted(geocodes), ordered=True)
        self.h_geocode_index = df['h_geocode'].astype(self.geocodes_cat).cat.codes
        self.w_geocode_index = df['w_geocode'].astype(self.geocodes_cat).cat.codes

        # Create dict of sparse matrices
        mat_dict = {k: coo_matrix((df[k], (self.w_geocode_index, self.h_geocode_index)), shape=shape) for k in jobs}

        # Stack into an n*n*k sparse coordinatate (COO) matrix
        # where n is the number of zones and k are the strata
        self.sparse_mat = sparse.stack([sparse.COO(m) for m in mat_dict.values()], axis=-1)

