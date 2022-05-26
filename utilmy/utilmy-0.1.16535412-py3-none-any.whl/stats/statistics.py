# coding=utf-8
"""# 
Doc::

    Hypothesis testing easy.

    https://github.com/pranab/beymani

    https://github.com/topics/hypothesis-testing?l=python&o=desc&s=stars

    https://pypi.org/project/pysie/#description



"""
import os, sys, pandas as pd, numpy as np
from utilmy.utilmy import pd_generate_data
from utilmy.prepro.util_feature import  pd_colnum_tocat, pd_colnum_tocat_stat

# conduct multiple comparisons
from tqdm import tqdm
from typing import List, Union
from scipy import stats


#################################################################################################
from utilmy.utilmy import log, log2

def help():
    """        .
    Doc::
            
    """
    from utilmy import help_create
    print( help_create("utilmy.stats.statistics") )


#################################################################################################
def test_all():
    """.
    Doc::
            
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
    ypred = model.predict(X_test)
    
    def test():
        log("Testing normality...")
        from utilmy.stats  import statistics as m
        error_test_normality(df["yield"])
        
        
        df1 = pd_generate_data(7, 100)
        m.test_anova(df1,'cat1','cat2')
        m.test_normality2(df1, '0', "Shapiro")
        m.test_plot_qqplot(df1, '1')

        
        log("Testing heteroscedacity...")
        log(m.error_test_heteroscedacity(y_test, ypred))
    
        log("Testing test_mutualinfo()...")
        df1 = pd_generate_data(7, 100)

        m.error_test_residual_mutualinfo(df1["0"], df1[["1", "2", "3"]], colname="test")

        log("Testing hypothesis_test()...")
        log(m.test_hypothesis(X_train, X_test,"chisquare"))

    def custom_stat(values, axis=1):
        #stat_val = np.mean(np.asmatrix(values),axis=axis)
        # # stat_val = np.std(np.asmatrix(values),axis=axis)p.mean
        stat_val = np.sqrt(np.mean(np.asmatrix(values*values),axis=axis))
        return stat_val

    def test_estimator():
        log("Testing estimators()...")
        from utilmy.stats.statistics import confidence_interval_normal_std,confidence_interval_boostrap_bayes,confidence_interval_bootstrap
        log(confidence_interval_normal_std(ypred))
        log(confidence_interval_boostrap_bayes(ypred))
        confidence_interval_bootstrap(ypred, custom_stat=custom_stat)



    def test_np_utils():
        log("Testing np_utils ...")
        from utilmy.stats.statistics import np_col_extractname, np_conv_to_one_col, np_list_remove
        import numpy as np
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        np_col_extractname(["aa_","bb-","cc"])
        np_list_remove(arr,[1,2,3], mode="exact")
        np_conv_to_one_col(arr)

  
    test()
    test_estimator()
    # test_drift_detect()
    test_np_utils()


def test0():
    """ .
    Doc::
            
    """
    df = pd_generate_data(7, 100)
    test_anova(df, 'cat1', 'cat2')
    test_normality2(df, '0', "Shapiro")
    test_plot_qqplot(df, '1')
    '''TODO: import needed
    NameError: name 'pd_colnum_tocat' is not defined
    test_mutualinfo(df["0"],df[["1","2","3"]],colname="test")
    '''


def test1():
    """        .
    Doc::
            
    """
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.model_selection import train_test_split

    df = pd.read_csv("../testdata/tmp/test/crop.data.csv")
    model = DecisionTreeRegressor(random_state=1)
    y = df.fertilizer
    X = df[["yield","density","block"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.50, random_state=42)
    model.fit(X_train, y_train)
    ypred = model.predict(X_test)
    error_test_normality(df["yield"])
    log(error_test_heteroscedacity(y_test, ypred))
    log(test_hypothesis(X_train, X_test,"chisquare"))
    log(confidence_interval_normal_std(ypred))
    log(confidence_interval_boostrap_bayes(ypred))
    '''TODO: need to check this one
    estimator_bootstrap(ypred, custom_stat=custom_stat(ypred))
    '''


def test3():
    """ .
    Doc::
            
    """
    arr = np.array([[1, 2, 3], [4, 5, 6]])
    np_col_extractname(["aa_","bb-","cc"])
    np_list_remove(arr,[1,2,3], mode="exact")
    np_conv_to_one_col(arr)


def test_check_mean():
    """function test_check_mean.
    Doc::
            
            Args:
            Returns:
                
    """
   
    n = 100
    df = pd.DataFrme({'id' :  np.arange(0, n)})
    df['c1'] = np.random.random(n ) 
    df['c2'] = np.random.random(n ) 
    df['c3'] = np.random.random(n ) 
    df['c4'] = np.random.random(n ) 
    df['c5'] = np.random.random(n ) 


    log("### 2 columns")
    test_same_mean(df, cols = [ 'c1', 'c2' ], bonferroni_adjuster=False, threshold=0.1, pcritic=0.5 )


    log("### 5 columns ")
    test_same_mean(df, cols=[ 'c1', 'c2', 'c3','c4','c5' ],  bonferroni_adjuster=False, threshold=0.1, pcritic=0.5)


    log("### 6 columsn not same")
    df['d6'] = np.random.random(n ) +0.3     
    test_same_mean(df, cols=[ 'c1', 'c2', 'c3','c4','d6' ], bonferroni_adjuster=True, threshold=0.1, pcritic=0.5  )






###############################################################################################
########## Helpers on test  ###################################################################
def test_same_mean(df: pd.DataFrame, cols=None, bonferroni_adjuster=True, threshold=0.1, pcritic=0.5) -> List[float]:
    """Test if same mean for all columns
    Doc::

       https://towardsdatascience.com/why-is-anova-essential-to-data-science-with-a-practical-example-615de10ba310
    """
    p_values = []
    cols = df.columns  if cols is None else cols

    if len(cols) == 2:
        log("## Student test of mean for 2 variables")
        p_values = test_student_mean(df, cols[0], cols[1], pcritic=pcritic,)

    else :   ##> 3 values
        log("## ANOVA test of mean for >2 variables")
        p_values = test_anova_mean(df, cols)

    if bonferroni_adjuster:
        p_values = bonferoni_adjuster(p_values, threshold=threshold)

    pvalue= p_values['p_value']
    if pvalue < pcritic:
        print("H0 hypothesis is rejected...", pvalue )
    else:
        print("H0 hypothesis is accepted...")

    return p_values



def test_independance(df: pd.DataFrame, cols=None, bonferroni_adjuster=True, threshold=0.1) -> List[float]:
    """Run ANOVA Test of independance.
    Doc::
            
        
    """
    p_values = []
    cols = df.columns  if cols is None else cols

    p_values = test_anova(df, cols)

    if bonferroni_adjuster:
        p_values = bonferoni_adjuster(p_values, threshold=threshold)

    return p_values





def test_independance_Xinput_vs_ytarget(df: pd.DataFrame, colsX=None, coly='y', bonferroni_adjuster=True, threshold=0.1) -> List[float]:
    """Run multiple T tests of Independance.
    Doc::
            
               p_values = multiple_comparisons(data)
               
        
        
    """
    p_values = []
    colsX = df.columns  if colsX is None else colsX
    for c in colsX:
        if c.startswith(coly):
            continue
        group_a = df[df[c] == 0][coly]
        group_b = df[df[c] == 1][coly]

        _, p = stats.ttest_ind(group_a, group_b, equal_var=False)
        p_values.append((c, p) )
    
    if bonferroni_adjuster:
        p_values = bonferoni_adjuster(p_values, threshold=threshold)

    return p_values




def bonferoni_adjuster(p_values, threshold=0.1):
    """Bonferroni correction.
    Doc::

        print('Total number of discoveries is: {:,}'  .format(sum([x[1] < threshold / n_trials for x in p_values])))
        print('Percentage of significant results: {:5.2%}'  .format(sum([x[1] < threshold / n_trials for x in p_values]) / n_trials))

        # Benjamini–Hochberg procedure
        p_values.sort(key=lambda x: x[1])

        for i, x in enumerate(p_values):
            if x[1] >= (i + 1) / len(p_values) * threshold:
                break
        significant = p_values[:i]

        print('Total number of discoveries is: {:,}' .format(len(significant)))
        print('Percentage of significant results: {:5.2%}'.format(len(significant) / n_trials))
    """
    p_values.sort(key=lambda x: x[1])
    for i, x in enumerate(p_values):
        if x[1] >= (i + 1) / len(p_values) * threshold:
            break
    pvalues_significant = p_values[:i]
    return pvalues_significant







#################################################################################################
############ Actual tests########################################################################
def test_chisquare(df_obs:pd.DataFrame, df_true:pd.DataFrame, method='chisquare', **kw):
    """ Hypothesis betweeb Obs and true values.
    Doc::
            
        
                https://github.com/aschleg/hypothetical/blob/master/tests/test_contingency.py
    """
    try:
       from utilmy.stats.hypothesis.contingency import (ChiSquareContingency, CochranQ, McNemarTest,
            table_margins, expected_frequencies )
    except :
       print(' pip install hypothesis ')

    if method == 'chisquare' :
        c = ChiSquareContingency(df_obs, df_true)
        return c



def test_anova(df:pd.DataFrame, col1, col2):
    """.
    Doc::
            
            ANOVA test two categorical features
            Input dfframe, 1st feature and 2nd feature
    """
    import scipy.stats as stats

    ov=pd.crosstab(df[col1],df[col2])

    dfb       = df[[col1, col2]]
    groups    = dfb.groupby(col1).groups
    edu_class = dfb[col2]
    lis_group = groups.keys()
    lg=[]
    for i in groups.keys():
        globals()[i]  = edu_class[groups[i]].values
        lg.append(globals()[i])

    dfd = 0
    for m in lis_group:
        dfd=len(m)-1+dfd
    print(stats.f_oneway(*lg))

    stat_val = stats.f_oneway(*lg)[0]
    crit_val = stats.f.ppf(q=1-0.05, dfn=len(lis_group)-1, dfd=dfd)
    if stat_val >= crit_val :
         print('Reject null hypothesies and conclude that atleast one group is different and the feature is releavant to the class.')
    else:
         print('Accept null hypothesies and conclude that atleast one group is same and the feature is not releavant to the class.')
    return { 'stat_val': stat_val, 'crit_val': crit_val  }


def test_normality2(df:pd.DataFrame, column, test_type):
    """.
    Doc::
            
            Function to check Normal Distribution of a Feature by 3 methods
            Input dfframe, feature name, and a test type
            Three types of test
            1)'Shapiro'
            2)'Normal'
            3)'Anderson'
        
            output the statistical test score and result whether accept or reject
            Accept mean the feature is Gaussain
            Reject mean the feature is not Gaussain
    """
    from scipy.stats import shapiro
    from scipy.stats import normaltest
    from scipy.stats import anderson
    if  test_type == 'Shapiro':
        stat, p = shapiro(df[column])
        print('Statistics=%.3f, p=%.3f' % (stat, p))
        # interpret
        alpha = 0.05
        if p > alpha:
            print(column,' looks Gaussian (fail to reject H0)')
        else:
            print(column,' does not look Gaussian (reject H0)')
    if  test_type == 'Normal':
        stat, p = normaltest(df[column])
        print('Statistics=%.3f, p=%.3f' % (stat, p))
        # interpret
        alpha = 0.05
        if p > alpha:
            print(column,' looks Gaussian (fail to reject H0)')
        else:
            print(column,' does not look Gaussian (reject H0)')
        # normality test
    if  test_type == 'Anderson':
        result = anderson(df[column])
        print('Statistic: %.3f' % result.statistic)
        p = 0
        for i in range(len(result.critical_values)):
            sl, cv = result.significance_level[i], result.critical_values[i]
            if result.statistic < result.critical_values[i]:
                print(sl,' : ',cv,' ',column,' looks normal (fail to reject H0)')
            else:
                print(sl,' : ',cv,' ',column,' does not looks normal (fail to reject H0)')



def test_plot_qqplot(df:pd.DataFrame, col_name):
    """.
    Doc::
            
            Function to plot boxplot, histplot and qqplot for numerical feature analyze
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    import statsmodels.api as sm
    fig, axes = plt.subplots(1, 3, figsize=(18,5))
    fig.suptitle('Numerical Analysis'+" "+col_name)
    sns.boxplot(ax=axes[0], data=df,x=col_name)
    sns.histplot(ax=axes[1],data=df, x=col_name, kde=True)
    sm.qqplot(ax=axes[2],data=df[col_name], line ='45')
    print(df[col_name].describe())



def test_mutualinfo(error, Xtest, colname=None, bins=5):
    """.
    Doc::
            
               Test  Error vs Input Variable Independance byt Mutual ifno
               sklearn.feature_selection.mutual_info_classif(X, y, discrete_features='auto', n_neighbors=3, copy=True, random_state=None)
        
    """
    from sklearn.feature_selection import mutual_info_classif
    error = pd.DataFrame({"error": error})
    error_dis, _ = pd_colnum_tocat(error, bins=bins, method="quantile")
    # print(error_dis)

    res = mutual_info_classif(Xtest.values, error_dis.values.ravel())

    return dict(zip(colname, res))




####################################################################################################
############ Residual error ########################################################################
def error_test_heteroscedacity(ypred: np.ndarray, ytrue: np.ndarray, pred_value_only=1):
    """function test_heteroscedacity.
    Doc::
            
            Args:
                ytrue:   
                ypred:   
                pred_value_only:   
            Returns:
                
    """
    ss = """
       Test  Heteroscedacity :  Residual**2  = Linear(X, Pred, Pred**2)
       F pvalues < 0.01 : Null is Rejected  ---> Not Homoscedastic
       het_breuschpagan

    """
    from statsmodels.stats.diagnostic import het_breuschpagan, het_white
    error    = ypred - ytrue

    ypred_df = pd.DataFrame({"pcst": [1.0] * len(ytrue), "pred": ypred, "pred2": ypred * ypred})
    labels   = ["LM Statistic", "LM-Test p-value", "F-Statistic", "F-Test p-value"]
    test1    = het_breuschpagan(error * error, ypred_df.values)
    test2    = het_white(error * error, ypred_df.values)
    ddict    = {"het-breuschpagan": dict(zip(labels, test1)),
             "het-white": dict(zip(labels, test2)),
             }

    return ddict


def error_test_normality(ypred: np.ndarray, ytrue: np.ndarray, distribution="norm", test_size_limit=5000):
    """.
    Doc::
            
               Test  Is Normal distribution
               F pvalues < 0.01 : Rejected
        
    """
    from scipy.stats import shapiro, anderson, kstest
    

    error2 = ypred -  ytrue

    error2 = error2[np.random.choice(len(error2), 5000)]  # limit test
    test1  = shapiro(error2)
    ddict1 = dict(zip(["shapiro", "W-p-value"], test1))

    test2  = anderson(error2, dist=distribution)
    ddict2 = dict(zip(["anderson", "p-value", "P critical"], test2))

    test3  = kstest(error2, distribution)
    ddict3 = dict(zip(["kstest", "p-value"], test3))

    ddict  = dict(zip(["shapiro", "anderson", "kstest"], [ddict1, ddict2, ddict3]))

    return ddict


def error_test_residual_mutualinfo(dfX:pd.DataFrame, ypred: np.ndarray, ytrue: np.ndarray, colsX=None, bins=5):
    """.
    Doc::
            
               Test  Error vs Input X Variable Independance byt Mutual ifno
               sklearn.feature_selection.mutual_info_classif(X, y, discrete_features='auto', n_neighbors=3, copy=True, random_state=None)
        
    """
    from sklearn.feature_selection import mutual_info_classif
    dferror = pd.DataFrame({"error": ypred - ytrue })
    error_dis, _ = pd_colnum_tocat(dferror, bins=bins, method="quantile")
    # print(error_dis)

    colsX = colsX if colsX is not None else dfX.columns
    dfX = dfX[colsX].values
    res = mutual_info_classif(dfX, error_dis.values.ravel())

    return dict(zip(colsX, res))






####################################################################################################
######### Confidence interval ######################################################################
def confidence_interval_normal_std(err:np.ndarray, alpha=0.05, ):
    """function estimator_std_normal.
    Doc::
            
            Args:
                err:   
                alpha:   confidence level
                :   
            Returns:   std_err, 
                
    """
    # estimate_std( err, alpha=0.05, )
    from scipy import stats
    n = len(err)  # sample sizes
    s2 = np.var(err, ddof=1)  # sample variance
    df = n - 1  # degrees of freedom
    upper = np.sqrt((n - 1) * s2 / stats.chi2.ppf(alpha / 2, df))
    lower = np.sqrt((n - 1) * s2 / stats.chi2.ppf(1 - alpha / 2, df))

    return np.sqrt(s2), (lower, upper)


def confidence_interval_boostrap_bayes(err:np.ndarray, alpha=0.05, ):
    """function estimator_boostrap_bayes.
    Doc::
            
            Args:
                err:   
                alpha:   
                :   
            Returns:
                
    """
    from scipy.stats import bayes_mvs
    mean, var, std = bayes_mvs(err, alpha=alpha)
    return mean, var, std


def confidence_interval_bootstrap(err:np.ndarray, custom_stat=None, alpha=0.05, n_iter=10000):
    """.
    Doc::
            
              def custom_stat(values, axis=1):
              # stat_val = np.mean(np.asmatrix(values),axis=axis)
              # stat_val = np.std(np.asmatrix(values),axis=axis)p.mean
              stat_val = np.sqrt(np.mean(np.asmatrix(values*values),axis=axis))
              return stat_val
    """
    try :
       import bootstrapped.bootstrap as bs
    except:
        log('pip install bootsrapped') ; 1/0
    res = bs.bootstrap(err, stat_func=custom_stat, alpha=alpha, num_iterations=n_iter)
    return res




####################################################################################################
####### Utils ######################################################################################
def np_col_extractname(col_onehot):
    """.
    Doc::
            
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
    """.
    Doc::
            
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


def np_conv_to_one_col(np_array, sep_char="_"):
    """.
    Doc::
            
            converts string/numeric columns to one string column
            np_array: the numpy array with more than one column
            sep_char: the separator character
    """
    def row2string(row_):
        return sep_char.join([str(i) for i in row_])

    np_array_=np.apply_along_axis(row2string,1,np_array)
    return np_array_[:,None]



if __name__ == '__main__':
    import fire
    fire.Fire()

