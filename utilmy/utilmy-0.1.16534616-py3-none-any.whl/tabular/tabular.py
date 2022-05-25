# coding=utf-8
"""Data Drift
Doc::


    https://thirdeyedata.io/unsupervised-concept-drift-detection-techniques-for-machine-learning-models-with-examples-in-python/

    https://github.com/pranab/beymani


    https://pkghosh.wordpress.com/2020/12/24/concept-drift-detection-techniques-with-python-implementation-for-supervised-machine-learning-models/

    https://github.com/topics/hypothesis-testing?l=python&o=desc&s=stars

    https://pypi.org/project/pysie/#description


"""
import os, sys, pandas as pd, numpy as np
from utilmy.utilmy import pd_generate_data
from utilmy.prepro.util_feature import  pd_colnum_tocat, pd_colnum_tocat_stat


#################################################################################################
from utilmy.utilmy import log, log2

def help():
    from utilmy import help_create
    print( help_create("utilmy.tabular") )

    
    
#################################################################################################
def test_all():
    """ python test.py   test_tabular
    """
    import pandas as pd
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.model_selection import train_test_split
    model = DecisionTreeRegressor(random_state=1)

    df = pd.read_csv("./testdata/tmp/test/crop.data.csv")
    y = df.fertilizer
    X = df[["yield","density","block"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.50, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    def test():
        df1 = pd_generate_data(7, 100)




    def custom_stat(values, axis=1):
        #stat_val = np.mean(np.asmatrix(values),axis=axis)
        # # stat_val = np.std(np.asmatrix(values),axis=axis)p.mean
        stat_val = np.sqrt(np.mean(np.asmatrix(values*values),axis=axis))
        return stat_val

       
    
    def test_pd_utils():
        log("Testing pd_utils ...")
        from utilmy.tabular import pd_train_test_split_time,pd_to_scipy_sparse_matrix,pd_stat_correl_pair,\
            pd_stat_pandas_profile,pd_stat_distribution_colnum,pd_stat_histogram,pd_stat_shift_trend_changes,\
            pd_stat_shift_trend_correlation,pd_stat_shift_changes
        from utilmy.prepro.util_feature import pd_colnum_tocat_stat

        pd_train_test_split_time(df, coltime="block")
        pd_to_scipy_sparse_matrix(df)
        '''TODO: git test failling here
        this bug is caused due to typecasting mismatch in the function.
        However, even typecasting the arrays manually in the function is not solving
        the problem.
        '''
        # log(pd_stat_correl_pair(df,coltarget=["fertilizer"],colname=["yield"]))
        
        pd_stat_pandas_profile(df,savefile="./testdata/tmp/test/report.html", title="Pandas profile")
        pd_stat_distribution_colnum(df, nrows=len(df))
        pd_stat_histogram(df, bins=50, coltarget="yield")
        _,df_grouped = pd_colnum_tocat_stat(df,"density","block",10)
        pd_stat_shift_trend_changes(df_grouped,"density","block")

        _, X_train_grouped =  pd_colnum_tocat_stat(X_train,"yield","block",10)
        _, X_test_grouped =  pd_colnum_tocat_stat(X_test,"yield","block",10)
        pd_stat_shift_trend_correlation(X_train_grouped, X_test_grouped,"yield","block")

        '''TODO: TypeError: pd_colnum_tocat_stat() got an unexpected keyword argument 'colname',
        This function needs complete rewrite there are many bugs and logical errors.
        pd_stat_shift_changes(df,"yield", features_list=["density","block"])
        '''



    def test_np_utils():
        log("Testing np_utils ...")
        from utilmy.tabular import np_col_extractname, np_conv_to_one_col, np_list_remove
        import numpy as np
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        np_col_extractname(["aa_","bb-","cc"])
        np_list_remove(arr,[1,2,3], mode="exact")
        np_conv_to_one_col(arr)

  
    test()
    test_pd_utils()
    # test_drift_detect()
    test_np_utils()



def test1():
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.model_selection import train_test_split

    df = pd.read_csv("../testdata/tmp/test/crop.data.csv")
    model = DecisionTreeRegressor(random_state=1)
    y = df.fertilizer
    X = df[["yield","density","block"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.50, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    '''TODO: need to check this one
    estimator_bootstrap(y_pred, custom_stat=custom_stat(y_pred))
    '''
    pd_train_test_split_time(df, coltime="block")
    pd_to_scipy_sparse_matrix(df)
    '''TODO: git test failling here'''
    #log(pd_stat_correl_pair(df,coltarget=["fertilizer"],colname=["yield"]))

    # pd_stat_pandas_profile(df,savefile="./testdata/tmp/test/report.html", title="Pandas profile")

    pd_stat_distribution_colnum(df, nrows=len(df))
    '''TODO: KeyError: 'freqall
    pd_stat_histogram(df, bins=50, coltarget="yield")
    '''
    ''' TODO: error KeyError: 'colname_mean' , why we appending '_mean' on colname 
    pd_stat_shift_trend_changes(df,"density","block")
    '''
    X_train["yield"] =  X_train["yield"].astype('category')
    X_test["yield"] =  X_test["yield"].astype('category')
    '''TODO: KeyError: "['block_mean'] not in index
    pd_stat_shift_trend_correlation(X_train, X_test,"yield","block")
    '''
    '''TODO: TypeError: pd_colnum_tocat_stat() got an unexpected keyword argument 'colname'
    pd_stat_shift_changes(df,"yield", features_list=["density","block"])
    '''


def test3():
    arr = np.array([[1, 2, 3], [4, 5, 6]])
    np_col_extractname(["aa_","bb-","cc"])
    np_list_remove(arr,[1,2,3], mode="exact")
    np_conv_to_one_col(arr)




#############################################################################
#############################################################################
def y_adjuster_log(y_true, y_pred_log, error_func, **kwargs):
    """Adjustment of log, exp transfrmation for yt= y + error
    Doc::

       https://www.inovex.de/de/blog/honey-i-shrunk-the-target-variable/       
       log(y) = u =sigma**2 due to convexity
    
    """
    import scipy as sp

    def cost_func(delta):
        return error_func(np.exp(delta + y_pred_log), y_true)

    res = sp.optimize.minimize(cost_func, 0., **kwargs)
    if res.success:
        return res.x
    else:
        raise RuntimeError(f"Finding correction term failed!\n{res}")



#############################################################################################################
def pd_train_test_split_time(df, test_period = 40, cols=None , coltime ="time_key", sort=True, minsize=5,
                     n_sample=5,  verbose=False) :
   cols = list(df.columns) if cols is None else cols
   if sort :
       df   = df.sort_values( coltime, ascending=1 )
   #imax = len(df) - test_period
   colkey = [ t for t in cols if t not in [coltime] ]  #### All time reference be removed
   if verbose : log(colkey)
   imax = test_period * n_sample ## Over sampling
   df1  = df.groupby( colkey ).apply(lambda dfi : dfi.iloc[:max(minsize, len(dfi) -imax), :] ).reset_index(colkey, drop=True).reset_index(drop=True)
   df2  = df.groupby( colkey ).apply(lambda dfi : dfi.iloc[max(minsize,  len(dfi) -imax):, :] ).reset_index(colkey, drop=True).reset_index(drop=True)
   return df1, df2


def pd_to_scipy_sparse_matrix(df):
    """Converts a sparse pandas data frame to sparse scipy csr_matrix.
        df: pandas data frame
        :return: csr_matrix
    """
    import numpy as np
    from scipy.sparse import lil_matrix
    arr = lil_matrix(df.shape, dtype=np.float32)
    for i, col in enumerate(df.columns):
        ix = df[col] != 0
        arr[np.where(ix), i] = 1

    return arr.tocsr()


def pd_stat_correl_pair(df, coltarget=None, colname=None):
    """
      Genearte correletion between the column and target column
      df represents the dataframe comprising the column and colname comprising the target column
    df:
    colname: list of columns
    coltarget : target column
    :return:
    """
    from scipy.stats import pearsonr

    colname = colname if colname is not None else list(df.columns)
    target_corr = []
    for col in colname:
        targets = df[coltarget].astype('float64')
        target_corr.append(pearsonr(df[col], targets)[0])

    df_correl = pd.DataFrame({"colx": [""] * len(colname), "coly": colname, "correl": target_corr})
    df_correl[coltarget] = colname
    return df_correl


def pd_stat_pandas_profile(df, savefile="report.html", title="Pandas Profile"):
    """ Describe the tables
        #Pandas-Profiling 2.0.0
        df.profile_report()
    """
    from pandas_profiling import ProfileReport
    print("start profiling")
    profile = df.profile_report(title=title)
    profile.to_file(output_file=savefile)
    colexclude = profile.get_rejected_variables()
    return colexclude


def pd_stat_distribution_colnum(df, nrows=2000, verbose=False):
    """ Stats the tables
    """
    df = df.sample(n=nrows)
    coldes = ["col", "coltype",  "count", "min", "max",  "median", "mean",
              "std", "25%", "75%", "nb_na", "pct_na" ]

    def getstat(col):
        """max, min, nb, nb_na, pct_na, median, qt_25, qt_75,
           nb, nb_unique, nb_na, freq_1st, freq_2th, freq_3th
           s.describe()
        """
        ss    = [col, str(df[col].dtype)]
        ss    = ss +list(df[col].describe().values)

        nb_na = df[col].isnull().sum()
        ntot  = len(df)
        ss    = ss + [nb_na, nb_na / (ntot + 0.0)]

        return pd.DataFrame( [ss],  columns=coldes, )

    dfdes = pd.DataFrame([], columns=coldes)
    cols  = df.columns
    for col in cols:
        dtype1 = str(df[col].dtype)
        if dtype1[0:3] in ["int", "flo"]:
            try :
              row1  = getstat(col)
              dfdes = pd.concat((dfdes, row1), axis=0)
            except Exception as e:
              print('error', col, e)

        if dtype1 == "object":
            pass

    dfdes.index = np.arange(0, len(dfdes))
    if verbose : print('Stats\n', dfdes)
    return dfdes


def pd_stat_histogram(df, bins=50, coltarget="diff"):
    """
    df:
    bins:
    coltarget:
    :return:
    """
    hh = np.histogram(
        df[coltarget].values, bins=bins, range=None, normed=None, weights=None, density=None
    )
    hh2 = pd.DataFrame({"bins": hh[1][:-1], "freq": hh[0]})
    # hh2["density"] = hh2["freqall"] / hh2["freqall"].sum()
    hh2["density"] = hh2["freq"] / hh2["freq"].sum()
    return hh2


def np_col_extractname(col_onehot):
    """
    Column extraction from onehot name
    col_onehotp
    :return:
    """
    colnew = []
    for x in col_onehot:
        if len(x) > 2:
            if x[-2] == "_":
                if x[:-2] not in colnew:
                    colnew.append(x[:-2])

            elif x[-2] == "-":
                if x[:-3] not in colnew:
                    colnew.append(x[:-3])

            else:
                if x not in colnew:
                    colnew.append(x)
    return colnew


def np_list_remove(cols, colsremove, mode="exact"):
    """
    """
    if mode == "exact":
        for x in colsremove:
            try:
                cols.remove(x)
            except BaseException:
                pass
        return cols

    if mode == "fuzzy":
        cols3 = []
        for t in cols:
            flag = 0
            for x in colsremove:
                if x in t:
                    flag = 1
                    break
            if flag == 0:
                cols3.append(t)
        return cols3


####################################################################################################
def pd_stat_shift_trend_changes(df, feature, target_col, threshold=0.03):
    """
    Calculates number of times the trend of feature wrt target changed direction.
    df: df_grouped dataset
    feature: feature column name
    target_col: target column
    threshold: minimum % difference required to count as trend change
    :return: number of trend chagnes for the feature
    """
    df                            = df.loc[df[feature] != 'Nulls', :].reset_index(drop=True)
    target_diffs                  = df[target_col + '_mean'].diff()
    target_diffs                  = target_diffs[~np.isnan(target_diffs)].reset_index(drop=True)
    max_diff                      = df[target_col + '_mean'].max() - df[target_col + '_mean'].min()
    target_diffs_mod              = target_diffs.fillna(0).abs()
    low_change                    = target_diffs_mod < threshold * max_diff
    target_diffs_norm             = target_diffs.divide(target_diffs_mod)
    target_diffs_norm[low_change] = 0
    target_diffs_norm             = target_diffs_norm[target_diffs_norm != 0]
    target_diffs_lvl2             = target_diffs_norm.diff()
    changes                       = target_diffs_lvl2.fillna(0).abs() / 2
    tot_trend_changes             = int(changes.sum()) if ~np.isnan(changes.sum()) else 0
    return (tot_trend_changes)


def pd_stat_shift_trend_correlation(df, df_test, colname, target_col):
    """
    Calculates correlation between train and test trend of colname wrt target.
    df: train df data
    df_test: test df data
    colname: colname column name
    target_col: target column name
    :return: trend correlation between train and test
    """
    df[colname] = df[colname].astype('category')
    df      = df[df[colname] != 'Nulls'].reset_index(drop=True)
    df_test = df_test[df_test[colname] != 'Nulls'].reset_index(drop=True)

    if df_test.loc[0, colname] != df.loc[0, colname]:
        df_test[colname]        = df_test[colname].cat.add_categories(df.loc[0, colname])
        df_test.loc[0, colname] = df.loc[0, colname]
    df_test_train = df.merge(df_test[[colname, target_col + '_mean']], on=colname,
                             how='left',
                             suffixes=('', '_test'))
    nan_rows = pd.isnull(df_test_train[target_col + '_mean']) | pd.isnull(
        df_test_train[target_col + '_mean_test'])

    df_test_train = df_test_train.loc[~nan_rows, :]
    if len(df_test_train) > 1:
        trend_correlation = np.corrcoef(df_test_train[target_col + '_mean'],
                                        df_test_train[target_col + '_mean_test'])[0, 1]
    else:
        trend_correlation = 0
        print("Only one bin created for " + colname + ". Correlation can't be calculated")

    return (trend_correlation)


def pd_stat_shift_changes(df, target_col, features_list=0, bins=10, df_test=0):
    """
    Calculates trend changes and correlation between train/test for list of features
    df: dfframe containing features and target columns
    target_col: target column name
    features_list: by default creates plots for all features. If list passed, creates plots of only those features.
    bins: number of bins to be created from continuous colname
    df_test: test df which has to be compared with input df for correlation
    :return: dfframe with trend changes and trend correlation (if test df passed)
    """

    if type(features_list) == int:
        features_list = list(df.columns)
        features_list.remove(target_col)

    stats_all = []
    has_test = type(df_test) == pd.core.frame.DataFrame
    ignored = []
    for colname in features_list:
        if df[colname].dtype == 'O' or colname == target_col:
            ignored.append(colname)
        else:
            cuts, df_grouped = pd_colnum_tocat_stat(df=df,feature=colname, target_col=target_col, bins=bins)
            trend_changes    = pd_stat_shift_trend_correlation(df=df_grouped,df_test=df_test, colname=colname, target_col=target_col)
            if has_test:
                df_test            = pd_colnum_tocat_stat(df=df_test.reset_index(drop=True), colname=colname,
                                                          target_col  = target_col, bins=bins, cuts=cuts)
                trend_corr         = pd_stat_shift_trend_correlation(df_grouped, df_test, colname, target_col)
                trend_changes_test = pd_stat_shift_changes(df=df_test, colname=colname,
                                                           target_col=target_col)
                stats = [colname, trend_changes, trend_changes_test, trend_corr]
            else:
                stats = [colname, trend_changes]
            stats_all.append(stats)
    stats_all_df = pd.DataFrame(stats_all)
    stats_all_df.columns = ['colname', 'Trend_changes'] if has_test == False else ['colname', 'Trend_changes',
                                                                                   'Trend_changes_test',
                                                                                   'Trend_correlation']
    if len(ignored) > 0:
        print('Categorical features ' + str(ignored) + ' ignored. Categorical features not supported yet.')

    print('Returning stats for all numeric features')
    return (stats_all_df)


def np_conv_to_one_col(np_array, sep_char="_"):
    """
    converts string/numeric columns to one string column
    np_array: the numpy array with more than one column
    sep_char: the separator character
    """
    def row2string(row_):
        return sep_char.join([str(i) for i in row_])

    np_array_=np.apply_along_axis(row2string,1,np_array)
    return np_array_[:,None]



#########################################################################
def pd_data_drift_detect_alibi(
    df:pd.DataFrame,      ### Reference dataset
    df_new:pd.DataFrame,  ### Test dataset to be checked
    method:str="'regressoruncertaintydrift','classifieruncertaintydrift','ksdrift','mmddrift','learnedkerneldrift','chisquaredrift','tabulardrift', 'classifierdrift','spotthediffdrift'",
    backend:str='tensorflow,pytorch',
    model=None,  ### Pre-trained model
    p_val=0.05,  **kwargs):
    
    """ Detecting drift in the dataset using alibi.
    Doc::

        https://docs.seldon.io/projects/alibi-detect/en/latest/api/modules.html
        
        df:      dfframe test dataset to check for drift
        dfnew:   dfframe test dataset to check for drift    
        backend: str "tensorflow" or "pytorch"
        model:   trained pytorch or tensorflow model.
        p_val:   p value float 

        example:
        model = tf.keras.Sequential([InputLayer(input_shape=(input_size)),Dropout(0.3),Dense(1)])
        model.compile(optimizer='adam',loss='mse')
        model.fit(X_train,y_train,epochs=1)

        cd, is_drift_preds = pd_data_drift_detect(X_train, X_test,'regressoruncertaintydrift','tensorflow',model=model)

        from utilmy import import_function
        myclass = import_function(fun_name='KSDrift', module_name='alibi_detect.cd')  
        mdrift = myclass(df.values,p_val=p_val,**kwargs)
    
    
    """
    methods = ['regressoruncertaintydrift','classifieruncertaintydrift','ksdrift',
                'mmddrift','learnedkerneldrift','chisquaredrift','tabulardrift',
                'classifierdrift','spotthediffdrift']
    
    if len(method) > 25 :
        log('Using KSDrift as default')
        method = 'ksdrift'
        backend = 'tensorflow'
        
    assert method in methods, f"method is invalid, methods available {methods}"

    from utilmy import import_function
    mc = import_function(fun_name= 'KSDrift', module_name='alibi_detect.cd')  
    mdrift = mc(df.values,p_val=p_val,**kwargs)
    
    
    if method == "regressoruncertaintydrift":
        from alibi_detect.cd import RegressorUncertaintyDrift as mc
        mdrift = mc(df.values,model=model,p_val=p_val, backend=backend,**kwargs)
    
    if method == 'classifieruncertaintydrift':
        from alibi_detect.cd import ClassifierUncertaintyDrift as mc
        mdrift = mc(df.values,model=model,p_val=p_val, backend=backend,preds_type='probs',**kwargs)
    
    if method == 'ksdrift':
        from alibi_detect.cd import KSDrift as mc
        mdrift = mc(df.values,p_val=p_val,**kwargs)
    
    if method == 'mmddrift':
        from alibi_detect.cd import MMDDrift as mc
        mdrift = mc(df.values,backend=backend,p_val=0.05,**kwargs)

    if method == 'learnedkerneldrift':
        from alibi_detect.cd import LearnedKernelDrift
        if backend == "tensforflow":
            from alibi_detect.utils.tensorflow.kernels import DeepKernel
            kernel = DeepKernel(model)
            mdrift = LearnedKernelDrift(df.values, kernel, backend=backend, p_val=p_val, **kwargs)
            
        if backend == "pytorch":
            from alibi_detect.utils.pytorch.kernels import DeepKernel
            kernel = DeepKernel(model)
            mdrift = LearnedKernelDrift(df.values, kernel, backend=backend, p_val=p_val, **kwargs)
    
    if method == 'chisquaredrift':
        from alibi_detect.cd import ChiSquareDrift as mc
        mdrift = mc(df.values, p_val=p_val,**kwargs)
    
    if method == 'tabulardrift':
        from alibi_detect.cd import TabularDrift as mc
        mdrift = mc(df.values, p_val=p_val,**kwargs)
    
    if method == 'classifierdrift':
        from alibi_detect.cd import ClassifierDrift as mc
        mdrift = mc(df.values, model, p_val=p_val,backend=backend,**kwargs)
    
    if method == 'spotthediffdrift':
        from alibi_detect.cd import SpotTheDiffDrift 

        if backend == 'tensorflow' and model is not None:
            from alibi_detect.utils.tensorflow.kernels import DeepKernel as mc
            kernel = mc(model)
            mdrift = SpotTheDiffDrift(df.values.astype('float32'),backend=backend,p_val=p_val,kernel=kernel)

        if backend == 'pytorch' and model is not None:
            from alibi_detect.utils.pytorch.kernels import DeepKernel as mc
            kernel = mc(model)
            mdrift = SpotTheDiffDrift(df.values.astype('float32'),backend=backend,p_val=p_val,kernel=kernel)
        
        mdrift = SpotTheDiffDrift(df.values.astype('float32'),backend=backend,p_val=p_val)

        
    is_drift_pvalue_scores = mdrift.predict(df_new.values)
    return mdrift, is_drift_pvalue_scores


 
    
    
    
