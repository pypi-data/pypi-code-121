# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
Refer to 
1. https://github.com/LinBaiTao/Supplier_Selection_Methods 
2.https://github.com/akestoridis/mcdm
"""

from importlib_metadata import entry_points
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'SimHei', 'mathtext.fontset': 'stix'})

###########################################################################################
###############################     1 Preprocessing         ###############################
###########################################################################################

####***************************     1.1 Normalization       ****************************###

def Normalize_Weights(weights_array,norm_type = 'divide_by_sum'):
    """Normalizes a provided weight array so that the sum equals 1

    Parameters
    ----------
    weights_array : a numpy array containing the raw weights
    
    norm_type : a string specifying the type of normalization to perform
        - 'divide_by_max' divides all values by the maximum value
        - 'divide_by_sum' divides all values by the sum of the values

    Yields
    ------
    temp_weights_array: a copy of the passed weights array with the normalizations performed

    Examples
    --------
    >>> import numpy as np
    >>> import mcdm_functions as mcfunc
    >>> criteria_weights = np.array([2,4,6,7,9])
    >>> temp = mcfunc.Normalize_Weights(criteria_weights,'divide_by_max')
    >>> print(temp)
    
        [ 0.22222222  0.44444444  0.66666667  0.77777778  1.        ]
    """   
    
    temp_weights_array = weights_array.copy()
    
    if norm_type is 'divide_by_max':
        temp_weights_array = temp_weights_array/temp_weights_array.max()

    elif norm_type is 'divide_by_sum':
        temp_weights_array = temp_weights_array/temp_weights_array.sum()
        
    else:
        print('You did not enter a valid type, so no changes were made')
    
    return temp_weights_array


###########################################################################################
def Normalize_Column_Scores(df, columns, norm_type = 'divide_by_max'):
    """Normalizes scores for specified columns in a pandas dataframe

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns
    
    columns: a list object that includes the columns to normalize
    
    norm_type : a string specifying the type of normalization to perform
        - 'divide_by_max' divides all values by the maximum value
        - 'range_norm' divides all values (+ the min) by the range of values in the column
        - 'z_norm' computes a z-score based on the mean and standard deviation of values
        - 'divide_by_sum' divides all values by the sum of the values
        - 'vector' dives all values by the square root of the sum of the squares of all values

    Yields
    ------
    temp_df: a copy of the passed dataframe with the normalizations performed

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> import mcdm_functions as mcfunc

    >>> data_dict = {'Product': ['A', 'B', 'C', 'D'],
                 'Product Advantage': [13.1,13.2,12.2,13.2],
                 'Strategic Alignment': [9.8,8.2,10.0,9.6],
                 'Technical Feasibility': [20.0,18.7,18.5,17.1],
                 'Market Attractiveness': [15.5,12.3,13.1,13.1]}
    >>> score_data = pd.DataFrame(data_dict)
    >>> score_data = score_data.set_index('Product')
    >>> print(score_data)
    
            Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                         15.5               13.1                  9.8   
    B                         12.3               13.2                  8.2   
    C                         13.1               12.2                 10.0   
    D                         13.1               13.2                  9.6   

             Technical Feasibility  
    Product                         
    A                         20.0  
    B                         18.7  
    C                         18.5  
    D                         17.1  
    
    
    >>> columns = ['Market Attractiveness','Product Advantage']
    >>> temp = mcfunc.Normalize_Column_Scores(score_data,columns)
    >>> print(temp)
    
             Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                     1.000000               13.1                  9.8   
    B                     0.793548               13.2                  8.2   
    C                     0.845161               12.2                 10.0   
    D                     0.845161               13.2                  9.6   

             Technical Feasibility  
    Product                         
    A                         20.0  
    B                         18.7  
    C                         18.5  
    D                         17.1  
    """   
    
    temp_df = df.copy()
    
    for column in columns:
        if norm_type is 'divide_by_max':
            max_entry = temp_df[column].max()
            temp_df[column] = temp_df[column]/max_entry
        
        elif norm_type is 'range_norm':
            min_entry = temp_df[column].min()
            max_entry = temp_df[column].max()
            temp_df[column] = (temp_df[column]-min_entry)/(max_entry - min_entry)
        
        elif norm_type is 'z_norm':
            mean = temp_df[column].mean()
            sd = temp_df[column].std()
            temp_df[column] = (temp_df[column]-mean)/sd
        
        elif norm_type is 'divide_by_sum':
            temp_df[column] = temp_df[column]/temp_df[column].sum()
            
        elif norm_type is 'vector':
            values = temp_df[column].values
            values_squared = values**2
            vector_norm = values/np.sqrt(np.sum(values_squared))
            temp_df[column] = vector_norm
        
        else:
            print('You did not enter a valid type, so no changes were made')
        
    return temp_df


####***************************     1.2 Conversion       ****************************###
def Convert_Higher_is_Better(df, columns, conversion_type = 'absolute'):
    """Converts scores given in a "lower is better" format to a "higher is better" format

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns
    
    columns: a list object that includes the columns to normalize
    
    conversion_type : a string specifying the type of conversion to perform
        - 'absolute' converts based on absolute scale
        - 'relative' converts based on relative scale
        - 'inverse'  converts based on its inverse value
        
    Yields
    ------
    temp_df: a copy of the passed dataframe with the conversions performed
    """
    
    
    temp_df = df.copy()
        
    for column in columns:
        if conversion_type.lower() is 'absolute':
            new_column = column+' (absolute HIB)'
            max_entry = temp_df[column].max()
            temp_df[new_column] = max_entry - temp_df[column]
    
        elif conversion_type.lower() is 'relative':
            new_column = column+' (relative HIB)'
            min_entry = temp_df[column].min()
            max_entry = temp_df[column].max()
            temp_df[new_column] = (max_entry - temp_df[column])/(max_entry-min_entry)
        
        elif conversion_type.lower() is 'inverse':
            new_column = column+' (inverse HIB)'
            temp_df[new_column] = 1/temp_df[column]

        else:
            print('You did not enter a valid type, so no changes were made')        
        
    return temp_df    


###########################################################################################
###############################     2 Weighting             ###############################
###########################################################################################

####***************************     2.1 Correlation         ****************************###

def abspearson(z_matrix):
    """ Calculate the absolute value of the Pearson correlation of the previded matrix.

    Parameters
    ----------
    z_matrix : a pandas or array object that contains specific columns

    
    Yields:
    -------
    abs_corr : a matrix of the Pearson correlation coefficients

    """
    
    # Make sure that the provided matrix is a float64 NumPy array
    z_matrix = np.array(z_matrix, dtype=np.float64)

    abs_corr = np.absolute(np.corrcoef(z_matrix, rowvar=False))

    return abs_corr


def pearson(z_matrix):
    """ Calculate the Pearson correlation coefficient of the provided matrix

    Parameters :
    ----------
    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    p_corr : the Pearson correlation coefficients of the provided matrix.
    """
    # Make sure that the provided matrix is a float64 NumPy array
    z_matrix = np.array(z_matrix, dtype=np.float64)

    p_corr = np.corrcoef(z_matrix, rowvar=False)
    return p_corr


def dcor(z_matrix):
    """ Calculate the distance correlation coefficients of the provided matrix
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    dcor_matrix : the distance correlation matrix

    """
    # Make sure that the provided matrix is a float64 NumPy array
    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Initialize the matrix for the distance correlation coefficients
    dcor_matrix = np.ones(
        (z_matrix.shape[1], z_matrix.shape[1]),
        dtype=np.float64,
    )

    # Compute the matrix of squared distance covariances
    dcov2_matrix = squared_dcov_matrix(z_matrix)

    # Compute the distance correlation coefficients
    for j_col in range(z_matrix.shape[1]):
        # Get the squared distance variance of the j-th criterion
        j_dvar2 = dcov2_matrix[j_col, j_col]

        for l_col in range(j_col + 1, z_matrix.shape[1]):
            # Get the squared distance variance of the l-th criterion
            l_dvar2 = dcov2_matrix[l_col, l_col]

            # Compare the product of their squared distance variances
            if j_dvar2 * l_dvar2 == 0.0:
                # The two criteria are independent
                dcor_matrix[j_col, l_col] = 0.0
                dcor_matrix[l_col, j_col] = 0.0
            else:
                # Get the squared distance covariance of the two criteria
                jl_dcov2 = dcov2_matrix[j_col, l_col]

                # Compute the squared distance correlation of the two criteria
                jl_dcor2 = squared_dcor(jl_dcov2, j_dvar2, l_dvar2)

                # Compute the distance correlation of the two criteria
                dcor_matrix[j_col, l_col] = np.sqrt(jl_dcor2)
                dcor_matrix[l_col, j_col] = dcor_matrix[j_col, l_col]

    return dcor_matrix


def squared_dcov_matrix(z_matrix):
    """ Calculate the matrix of squared distance covariance between the columns of
    the provided matrix.
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    dcor2_matrix : the matrix of squared distance covariance

    """
    # Initialize the distance covariance matrix
    dcov2_matrix = np.zeros(
        (z_matrix.shape[1], z_matrix.shape[1]),
        dtype=np.float64,
    )

    for j_col in range(z_matrix.shape[1]):
        # Compute the Euclidean distance matrix of the j-th criterion
        j_dmatrix = dist_matrix(z_matrix[:, j_col])

        # Compute the linear function of its Euclidean distance matrix
        j_func = lin_func(j_dmatrix)

        for l_col in range(j_col, z_matrix.shape[1]):
            if j_col == l_col:
                # Compute the distance variance of the j-th criterion
                dcov2_matrix[j_col, j_col] = squared_dcov(j_func, j_func)
            else:
                # Compute the Euclidean distance matrix of the l-th criterion
                l_dmatrix = dist_matrix(z_matrix[:, l_col])

                # Compute the linear function of its Euclidean distance matrix
                l_func = lin_func(l_dmatrix)

                # Compute the squared distance covariance of the two criteria
                dcov2_matrix[j_col, l_col] = squared_dcov(j_func, l_func)
                dcov2_matrix[l_col, j_col] = dcov2_matrix[j_col, l_col]

    return dcov2_matrix


def dist_matrix(z_vector):
    """ Calculate the Euclidean distance matrix of provided vector
    
    Parameters :
    ----------

    z_vector : a pandas or array object that contains specific columns

    Yields:
    -------
    d_matrix : the matrix of the Euclidean distance matrix

    """
    # Initialize the Euclidean distance matrix
    dmatrix = np.zeros(
        (z_vector.shape[0], z_vector.shape[0]),
        dtype=np.float64,
    )

    for i_row in range(z_vector.shape[0]):
        for k_row in range(i_row + 1, z_vector.shape[0]):
            # The Euclidean distance of two real-valued scalars corresponds
            # to the absolute value of their difference
            dmatrix[i_row, k_row] = np.fabs(z_vector[i_row] - z_vector[k_row])
            dmatrix[k_row, i_row] = dmatrix[i_row, k_row]

    return dmatrix


def lin_func(dmatrix):
    """ Calculate the result of the linear function for the provided distance matrix
    
    Parameters :
    ----------

    d_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    res : the result of the linear function for the provided distance matrix
.
    """
    res = dmatrix - np.mean(dmatrix, axis=0) - np.reshape(np.mean(dmatrix, axis=1), (dmatrix.shape[0], 1))+ np.mean(dmatrix)

    return res


def squared_dcov(j_func, l_func):
    """ Calculate the squared distance covariance between the corresponding columns
    
    Parameters :
    ----------
    j_func : an array type object
    l_func : another array type object

    Yields:
    -------
    sq_dcov : the squared distance covariance of j_func and l_func

    """
    sq_dov = np.sum(np.multiply(j_func, l_func)) / (j_func.shape[0] ** 2)
    return sq_dov


def squared_dcor(jl_dcov2, j_dvar2, l_dvar2):

    """ Calculate the squared distance correlation between the corresponding columns
    
    Parameters :
    ----------
    j1_dov2 : an array

    j_dvar2 : an array

    l_dvar2 : an array

    Yields:
    -------
    sq_dcor : the squared distance correlation

    """
    sq_dcor = jl_dcov2 / np.sqrt(j_dvar2 * l_dvar2)
    return sq_dcor



def correlate(z_matrix, c_method):
    """ Calculate the selected correlation coefficients of the provide matrix
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    c_method : the selected correlation method
        - "PEARSON" - Pearson correlation
        - "ABSPEARSON" - Absolute Pearson correlation
        - "DCOR" - Distance correlation

    Yields:
    -------
    the selected correlation cofficients

    """
    # Use the selected correlation method
    if c_method.upper() == "PEARSON":
        return pearson(z_matrix)
    elif c_method.upper() == "ABSPEARSON":
        return abspearson(z_matrix)
    elif c_method.upper() == "DCOR":
        return dcor(z_matrix)
    else:
        raise ValueError("Unknown correlation method ({})".format(c_method))


####***********************    2.2 Critic                     ****************###

def critic(z_matrix, c_method="Pearson"):
    """ Calculate the  weight vector of the provided matrix using the Criteria 
    Importance Through Intercriteria Correlation(CRITIC) method
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    c_method : the selected correlation method
        - "PEARSON" - Pearson correlation
        - "ABSPEARSON" - Absolute Pearson correlation
        - "DCOR" - Distance correlation

    Yields:
    -------
    critic_weights : the weight vector of CRITIC

    """
    # Perform sanity checks
    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Compute the standard deviation of each criterion
    sd_vector = np.std(z_matrix, axis=0, dtype=np.float64)

    # Compute the correlation coefficients between pairs of criteria
    corr_matrix = correlate(z_matrix, c_method)

    # Compute the importance of each criterion
    imp_vector = np.zeros(z_matrix.shape[1], dtype=np.float64)
    for j_col in range(z_matrix.shape[1]):
        tmp_sum = 0.0
        for l_col in range(z_matrix.shape[1]):
            tmp_sum += 1.0 - corr_matrix[j_col, l_col]
        imp_vector[j_col] = sd_vector[j_col] * tmp_sum
    
    # Normalize the importance of each criterion
    critic_weights = imp_vector / np.sum(imp_vector)
    return critic_weights


####***********************           2.3 Entropy                        ****************###

def em(z_matrix):
    """ Calculate the weight vector of the provided decision matrix using the Entropy
    Measure(EM) method
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    em_weights : the weight vector of EM

    """
    # Perform sanity checks
    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Compute the normalization constant
    k_constant = 1.0 / np.log(z_matrix.shape[0])

    # Compute the entropy of each criterion
    e_vector = np.zeros(z_matrix.shape[1], dtype=np.float64)
    for j in range(z_matrix.shape[1]):
        tmp_sum = 0.0
        for i in range(z_matrix.shape[0]):
            if z_matrix[i, j] > 0.0:
                tmp_sum += z_matrix[i, j] * np.log(z_matrix[i, j])
        e_vector[j] = -k_constant * tmp_sum

    # The importance of each criterion corresponds to
    # its normalized degree of divergence
    em_weights = (1.0 - e_vector) / np.sum(1.0 - e_vector)
    return em_weights


####***********************           2.4 Mean Weighting               ****************###
def mw(z_matrix):
    """ Calculate the the weight vector of the provided matrix using the Mean
    Weights(MW) method
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    mw_weights : the weight vector of MW

    """
    # Perform sanity checks
    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Each criterion is considered equally important
    mw_weights = np.full(z_matrix.shape[1], 1.0 / z_matrix.shape[1], dtype=np.float64)
    return mw_weights


####***********************           2.5 Standard Deviation Weighting               ****************###

def sd(z_matrix):
    """ Calculate the the weight vector of the provided matrix using the 
    Standard Deviation(SD) method
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    Yields:
    -------
    sd_weights : the weight vector of SD

    """

    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Compute the standard deviation of each criterion
    sd_vector = np.std(z_matrix, axis=0, dtype=np.float64)

    # The importance of each criterion corresponds to
    # its normalized standard deviation
    sd_weights = sd_vector / np.sum(sd_vector)
    return sd_weights


####******************   2.6  Variability and Interdependencies of Criteria method    ****************###

def vic(z_matrix, c_method="dCor"):
    """ Calculate the the weight vector of the provided matrix using the 
    Variablity and Interdependencies of Criteria(VIC) method.
    
    Parameters :
    ----------

    z_matrix : a pandas or array object that contains specific columns

    c_method : the selected correlation method
        - "DCOR" - Distance correlation (default parameter)
        - "PEARSON" - Pearson correlation
        - "ABSPEARSON" - Absolute Pearson correlation
        

    Yields:
    -------
    vic_weights : the weight vector of VIC

    """

    z_matrix = np.array(z_matrix, dtype=np.float64)
    if c_method is None:
        c_method = "dCor"

    # Compute the standard deviation of each criterion
    sd_vector = np.std(z_matrix, axis=0, dtype=np.float64)

    # Compute the correlation coefficients between pairs of criteria
    corr_matrix = correlate(z_matrix, c_method)

    # Compute the importance of each criterion
    imp_vector = np.zeros(z_matrix.shape[1], dtype=np.float64)
    for j_col in range(z_matrix.shape[1]):
        tmp_sum = 0.0
        for l_col in range(z_matrix.shape[1]):
            tmp_sum += corr_matrix[j_col, l_col]
        imp_vector[j_col] = sd_vector[j_col] / tmp_sum

    # Normalize the importance of each criterion
    return imp_vector / np.sum(imp_vector)


####******************   2.7  Analytic Hierachy Processing    ****************###
def ahp(judge_matrix):
    """ Calculate the weights using Analytic Hierachy Processing(AHP)
    
    Parameters :
    ----------

    judge_matrix : a pair-wise matrix
        
    Yields:
    -------
    ahp_weights : the weight vector of AHP

    """

    judge_matrix = np.array(judge_matrix, dtype=np.float64)
    n =  judge_matrix.shape[0]
    eigenvalues, eigenvectors = np.linalg.eig(judge_matrix)
    value_max = eigenvalues.max()
    value_max_index = eigenvalues.argmax()
    CI = (value_max-n)/(n-1)
    RI_list = [0,0,0,0.58,0.9,1.12,1.24,1.32,1.41,1.45,1.49] 
    if CI/RI_list[n]>0.1:
        return 'Judgement Matrix is NOT consistent'
    else:
        print('The Max Eigenvalue is ',value_max)
        ahp_weights = eigenvectors[:,value_max_index]
        ahp_weights = ahp_weights/ahp_weights.sum()
        return ahp_weights


###########################################################################################
###############################        3 MCDM Models        ###############################
###########################################################################################           
            
####***********************    3.1 Simple Additive Weighting scores     ****************###

def Compute_Weighted_Sum_Score(df,criteria_list,weights_array):
    """Computes weighted sum score for specified columns

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns and scores
    
    columns: a list object that includes the columns to include in the score
    
    weights_array : an array containing the weights for each column
    
    Yields
    ------
    temp_df: a sorted copy of the passed dataframe with the score in a 
    new column named 'Weighted Score (Sum)'

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> import mcdm_functions as mcfunc

    >>> data_dict = {'Product': ['A', 'B', 'C', 'D'],
                 'Product Advantage': [13.1,13.2,12.2,13.2],
                 'Strategic Alignment': [9.8,8.2,10.0,9.6],
                 'Technical Feasibility': [20.0,18.7,18.5,17.1],
                 'Market Attractiveness': [15.5,12.3,13.1,13.1]}
    >>> score_data = pd.DataFrame(data_dict)
    >>> score_data = score_data.set_index('Product')
    >>> print(score_data)
    
            Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                         15.5               13.1                  9.8   
    B                         12.3               13.2                  8.2   
    C                         13.1               12.2                 10.0   
    D                         13.1               13.2                  9.6   

             Technical Feasibility  
    Product                         
    A                         20.0  
    B                         18.7  
    C                         18.5  
    D                         17.1  
    
    >>> criteria = ['Market Attractiveness',
                    'Product Advantage',
                    'Strategic Alignment',
                    'Technical Feasibility']

    >>> criteria_weights = np.array([4,6,7,9])

    >>> temp = mcfunc.Compute_Weighted_Sum_Score(score_data,criteria,criteria_weights)
    >>> print(temp)
    
             Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                         15.5               13.1                  9.8   
    B                         12.3               13.2                  8.2   
    C                         13.1               12.2                 10.0   
    D                         13.1               13.2                  9.6   

             Technical Feasibility  Weighted Score (Sum)  
    Product                                               
    A                         20.0                 389.2  
    B                         18.7                 354.1  
    C                         18.5                 362.1  
    D                         17.1                 352.7  
       
    """   
    temp_df = df.copy()
    temp_weights = weights_array.copy()
    
    temp_df['Weighted Score (Sum)'] = 0
    for i in range(len(criteria_list)):
        current_criteria = criteria_list[i]
        current_weight = temp_weights[i]
        temp_df['Weighted Score (Sum)'] += current_weight*temp_df[current_criteria]
    
    temp_df.sort_values(by = 'Weighted Score (Sum)', ascending=False, inplace=True)
    return temp_df   



####***********************    3.2 Multiplicative Exponential Weighting scores     ****************###         
def Compute_Weighted_Product_Score(df,criteria_list,weights_array):
    """Computes weighted product score for specified columns

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns and scores
    
    columns: a list object that includes the columns to include in the score
    
    weights_array : an array containing the weights for each column
    
    Yields
    ------
    temp_df: a sorted copy of the passed dataframe with the score in a 
    new column named 'Weighted Score (Product)'

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> import mcdm_functions as mcfunc

    >>> data_dict = {'Product': ['A', 'B', 'C', 'D'],
                 'Product Advantage': [13.1,13.2,12.2,13.2],
                 'Strategic Alignment': [9.8,8.2,10.0,9.6],
                 'Technical Feasibility': [20.0,18.7,18.5,17.1],
                 'Market Attractiveness': [15.5,12.3,13.1,13.1]}
    >>> score_data = pd.DataFrame(data_dict)
    >>> score_data = score_data.set_index('Product')
    >>> print(score_data)
    
            Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                         15.5               13.1                  9.8   
    B                         12.3               13.2                  8.2   
    C                         13.1               12.2                 10.0   
    D                         13.1               13.2                  9.6   

             Technical Feasibility  
    Product                         
    A                         20.0  
    B                         18.7  
    C                         18.5  
    D                         17.1  
    
    >>> criteria = ['Market Attractiveness',
                    'Product Advantage',
                    'Strategic Alignment',
                    'Technical Feasibility']

    >>> criteria_weights = np.array([0.1, 0.2, 0.3, 0.4])

    >>> temp = mcfunc.Compute_Weighted_Product_Score(score_data,criteria,criteria_weights)
    >>> print(temp)
    
               Market Attractiveness  Product Advantage  Strategic Alignment  \
    Product                                                                  
    A                         15.5               13.1                  9.8   
    B                         12.3               13.2                  8.2   
    C                         13.1               12.2                 10.0   
    D                         13.1               13.2                  9.6   

             Technical Feasibility  Weighted Score (Product)  
    Product                                                   
    A                         20.0                 14.463295  
    B                         18.7                 13.061291  
    C                         18.5                 13.673125  
    D                         17.1                 13.296022   
       
    """   
    temp_df = df.copy()
    temp_weights = weights_array.copy()
    
    temp_df['Weighted Score (Product)'] = 1
    for i in range(len(criteria_list)):
        current_criteria = criteria_list[i]
        current_weight = temp_weights[i]
        temp_df['Weighted Score (Product)'] *= temp_df[current_criteria]**current_weight
    
    temp_df.sort_values(by = 'Weighted Score (Product)', ascending=False, inplace=True)
    return temp_df   


####****   3.3 Modified Technique for Order Preference by Similarity to Ideal Solution ********### 

def Compute_TOPSIS_Score(df,criteria_list,weights_array):
    '''This function computes a TOPSIS score for suppliers based on the specified criteria and weights
    
    
    """Computes weighted product score for specified columns

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns and scores
    
    columns: a list object that includes the columns to include in the score
    
    weights_array : an array containing the weights for each column
    
    Yields
    ------
    temp_df: a sorted copy of the passed dataframe with the score in a 
    new column named 'TOPSIS Score'
    
    Note
    ----
    This TOPSIS implementation does not perform any standardization of the alernative scores or weights. 
    We do this to allow the user to define and experiment with various methods of regularization.
    
    '''
    
    temp_df = df.copy()
    temp_weights_array = weights_array.copy()
    
    #Step 1
    evaluation_matrix = temp_df[criteria_list].values

    #Step 2
    #squared_evaluation_matrix = evaluation_matrix**2
    #normalized_evaluation_matrix = evaluation_matrix/np.sqrt(np.sum(squared_evaluation_matrix,axis=0))
    normalized_evaluation_matrix = evaluation_matrix

    #Step 3
    #temp_weights_array = temp_weights_array/temp_weights_array.sum()
    weighted_matrix = normalized_evaluation_matrix * temp_weights_array

    #Step 4
    PIS = np.max(weighted_matrix, axis=0)
    NIS = np.min(weighted_matrix, axis=0)

    #Step 5
    intermediate = (weighted_matrix - PIS)**2
    Dev_Best = np.sqrt(intermediate.sum(axis = 1))

    intermediate = (weighted_matrix - NIS)**2
    Dev_Worst = np.sqrt(intermediate.sum(axis = 1))

    #Step 6
    Closeness = Dev_Worst/(Dev_Best+Dev_Worst)

    #Step 7
    temp_df['TOPSIS Score'] = Closeness.tolist()
    temp_df.sort_values(by='TOPSIS Score',ascending=False,inplace=True)

    return temp_df


###########################################################################################
###############################        4 Robustness Test    ###############################
###########################################################################################  


##############################################################################
def Robust_Ranking(df, 
                   columns,
                   perturbations,
                   weights_array,
                   weights_min=0,
                   weights_max= 9999999999,
                   perturbation_range = 0.05,
                   weight_norm_method ='divide_by_sum',
                   score_type = 'weighted_sum',
                   top_values = 5,
                   include_plot=False
                  ):
    """Performs a robustness check for defined ranking methods

    Parameters
    ----------
    df : a pandas DataFrame object that contains the specified columns
    
    columns: a list object that includes the columns to include in the score
    
    weights_array: an array containing the weights for each column
    
    weights_min: The minimum aceptable value for weights
    
    weights_max: The maximum aceptable value for weights
    
    perturbation_range: The perturbation range to consider (expressed as a proportion of the mean value)
    
    weight_norm_method: A string specifying the method to use for normalization of perturbed weights
        - 'divide_by_max' divides all weights by the maximum weight
        - 'divide_by_sum' divides all weights by the sum of the weights
    
    score_type: A string specifying the type of score  calculation
        - 'weighted_sum' uses the weighted sum method
        - 'weighted_product' uses the weighted product method
        - 'topsis'
    
    top_values: specifies the number of alternatives to keep from each ranking (highest ranked scores kept)

    Yields
    ------
    sum_counts: dataframe indicating the proportion of times each alternative appears in top ranking
    """
    
    
    temp_perturbations = perturbations
    df_copy = df.copy()
    temp_columns_list = list(columns)
    temp_weights_array = weights_array.copy()
    
    weight_mean = temp_weights_array.mean()
    perturbation_amount = weight_mean*perturbation_range
            
    alter_list = []
    count_column_name = ''
    proportion_column_name = ''
       
    np.random.seed(42)

    for i in range(temp_perturbations):
        perturbation_vector = np.random.uniform(low = -1.0*perturbation_amount,
                                                high = perturbation_amount,
                                                size=len(weights_array))

        perturbed_weights = temp_weights_array + perturbation_vector
        perturbed_weights = np.maximum(perturbed_weights,weights_min)
        perturbed_weights = np.minimum(perturbed_weights,weights_max)
        
        if weight_norm_method == 'divide_by_sum':
            perturbed_weights = Normalize_Weights(perturbed_weights,'divide_by_sum')
        
        elif weight_norm_method == 'divide_by_max':
            perturbed_weights = Normalize_Weights(perturbed_weights,'divide_by_max')
        
        if score_type == 'weighted_sum':
            count_column_name = 'Weighted Sum Count'
            proportion_column_name = 'Weighted Sum Proportion'
            temp_df = Compute_Weighted_Sum_Score(df_copy,
                                                 temp_columns_list,
                                                 perturbed_weights)
            temp_df = temp_df.nlargest(top_values, columns = 'Weighted Score (Sum)')
            temp_list = temp_df.index.values.tolist()
            alter_list.append(temp_list)
            
        elif score_type == 'weighted_product':
            count_column_name = 'Weighted Product Count'
            proportion_column_name = 'Weighted Product Proportion'
            temp_df = Compute_Weighted_Product_Score(df_copy,
                                                 temp_columns_list,
                                                 perturbed_weights)
            temp_df = temp_df.nlargest(top_values, columns = 'Weighted Score (Product)')
            temp_list = temp_df.index.values.tolist()
            alter_list.append(temp_list)
            
        elif score_type == 'topsis':
            count_column_name = 'TOPSIS Count'
            proportion_column_name = 'TOPSIS Proportion'
            temp_df = Compute_TOPSIS_Score(df_copy,
                                           temp_columns_list,
                                           perturbed_weights)
            temp_df = temp_df.nlargest(top_values, columns = 'TOPSIS Score')
            temp_list = temp_df.index.values.tolist()
            alter_list.append(temp_list)
           
    
    sum_counts = Counter(x for sublist in alter_list for x in sublist)
    sum_counts = pd.DataFrame.from_dict(sum_counts,orient='index').reset_index()
    sum_counts = sum_counts.rename(columns={0:count_column_name})
    sum_counts.sort_values(by=count_column_name, ascending=False,inplace=True)
    sum_counts[proportion_column_name] = sum_counts[count_column_name]/(temp_perturbations)
    
    
    if include_plot is True:
        fig, ax = plt.subplots(1,1,figsize = (8,5))

        sum_counts.plot.bar(y=proportion_column_name,
                            ax = ax,
                            color = 'blue',
                            alpha = 0.5,
                            edgecolor = 'k')

        ax.set_title(proportion_column_name,fontsize = 20)
        ax.set_xlabel('Alternative',fontsize = 20)
        ax.set_ylabel('Proportion',fontsize = 20)
        ax.xaxis.set_tick_params(labelsize=15)
        ax.yaxis.set_tick_params(labelsize=15)

        ax.legend_.remove()
        plt.show()
    
    return sum_counts