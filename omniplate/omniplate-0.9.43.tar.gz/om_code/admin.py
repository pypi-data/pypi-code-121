# General admin functions
# generating and updating dataframes and the progress dictionary
import pandas as pd


def initialiseprogress(self, experiment):
    """
    Initialises progress dictionary.
    """
    self.progress["ignoredwells"][experiment] = []
    self.progress["negativevalues"][experiment] = False
    self.progress["gc"][experiment] = None


###


def makewellsdf(df_r):
    """
    Makes a dataframe that stores the contents of
    the wells
    """
    df = df_r[["experiment", "condition", "strain", "well"]].drop_duplicates()
    df = df.reset_index(drop=True)
    return df


###


def make_s(self, tmin=None, tmax=None):
    """
    Generate s datafram by calculating means and variances of all datatypes
    from raw data
    """
    # restrict time
    if tmin and not tmax:
        rdf = self.r[self.r.time >= tmin]
    elif tmax and not tmin:
        rdf = self.r[self.r.time <= tmax]
    elif tmin and tmax:
        rdf = self.r[(self.r.time >= tmin) & (self.r.time <= tmax)]
    else:
        rdf = self.r
    # find means
    df1 = (
        rdf.groupby(["experiment", "condition", "strain", "time"])
        .mean()
        .reset_index()
    )
    for exp in self.allexperiments:
        for dtype in self.datatypes[exp]:
            df1 = df1.rename(columns={dtype: dtype + " mean"})
    # find errors
    df2 = (
        rdf.groupby(["experiment", "condition", "strain", "time"])
        .std()
        .reset_index()
    )
    for exp in self.allexperiments:
        for dtype in self.datatypes[exp]:
            df2 = df2.rename(columns={dtype: dtype + " err"})
    return pd.merge(df1, df2)


###


def update_s(self):
    """
    Updates means and errors of all datatypes from raw data
    """
    # find tmin and tmax in case restrict_time has been called
    tmin = self.s.time.min()
    tmax = self.s.time.max()
    # recalculate s dataframe
    self.s = make_s(self, tmin, tmax)
###
