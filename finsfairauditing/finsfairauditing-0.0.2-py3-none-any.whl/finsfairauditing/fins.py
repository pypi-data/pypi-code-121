"""Metrics to assess the fairness of a subset selection
    References
    ----------
    Kathleen Cachel and Elke Rundensteiner.
    "FINS Auditing Framework: Group Fairness for Subset Selections"
    in the proceedings of the AAAI/ACM conference on Artificial Intelligence,
    Ethics, and Society (AIES 2022)
"""


# Authors: Kathleen Cachel <kcachel@wpi.edu>
# License: Apache Software Liscence 2.0


import numpy as np


# Function for error handling with group information
def check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups):
    """
        Check whether input pool, subset, and protected attribute information is valid.

        Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).

    Returns
    ----------
    Raise errors if found.
    """

    # error handling for types
    if not isinstance(pool_items, np.ndarray):
        raise TypeError("Input pool_items must be ndarray")

    if not isinstance(pool_scores, np.ndarray):
        raise TypeError("Input pool_scores must be ndarray")

    if not isinstance(pool_groups, np.ndarray):
        raise TypeError("Input pool_groups must be ndarray")

    if not isinstance(subset_items, np.ndarray):
        raise TypeError("Input subset_items must be ndarray")

    if not isinstance(subset_scores, np.ndarray):
        raise TypeError("Input subset_scores must be ndarray")

    if not isinstance(subset_groups, np.ndarray):
        raise TypeError("Input subset_groups must be ndarray")


    # error handling for inputs sizes and values
    if len(pool_items) <= 0:  # check size of input pool
        raise ValueError("Please input a valid pool")
    if len(subset_items) <= 0:  # check size of subset
        raise ValueError("Please input a valid subset")

    if len(pool_items) != len(pool_scores):  # check size of input pool and scores match
        raise ValueError("Please input a pool and scores of same size")

    if len(pool_items) != len(pool_groups):  # check size of input pool and groups match
        raise ValueError("Please input a pool and groups of same size")

    if len(subset_items) != len(subset_scores):  # check size of input subset and scores match
        raise ValueError("Please input a subset and scores of same size")

    if len(subset_items) != len(subset_groups):  # check size of input subset and groups match
        raise ValueError("Please input a subset and groups of same size")

    if len(set(pool_items)) != len(pool_items):  # check for repetition in input pool
        raise ValueError("Please input a pool with unique items")

    if len(set(subset_items)) != len(subset_items):  # check for repetition in subset
        raise ValueError("Please input a pool with unique items")

    if (np.min(np.unique(pool_groups)) != 0) or (np.max(np.unique(pool_groups)) != len(
            np.unique(pool_groups)) - 1):  # check for consecutive group encoding in pool
        raise ValueError("Please represent pool groups via consecutive integers 0,1,2, etc...")


# Function for error handling with group information
def check_pool_subset_items_groups(pool_items, pool_groups, subset_items, subset_groups):
    """
        Check whether input pool, subset, and protected attribute information is valid.

        Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).

    Returns
    ----------
    Raise errors if found.
    """

    # error handling for types
    if not isinstance(pool_items, np.ndarray):
        raise TypeError("Input pool_items must be ndarray")

    if not isinstance(pool_groups, np.ndarray):
        raise TypeError("Input pool_groups must be ndarray")

    if not isinstance(subset_items, np.ndarray):
        raise TypeError("Input subset_items must be ndarray")


    if not isinstance(subset_groups, np.ndarray):
        raise TypeError("Input subset_groups must be ndarray")


    # error handling for inputs sizes and values
    if len(pool_items) <= 0:  # check size of input pool
        raise ValueError("Please input a valid pool")
    if len(subset_items) <= 0:  # check size of subset
        raise ValueError("Please input a valid subset")

    if len(pool_items) != len(pool_groups):  # check size of input pool and groups match
        raise ValueError("Please input a pool and groups of same size")

    if len(subset_items) != len(subset_groups):  # check size of input subset and groups match
        raise ValueError("Please input a subset and groups of same size")

    if len(set(pool_items)) != len(pool_items):  # check for repetition in input pool
        raise ValueError("Please input a pool with unique items")

    if len(set(subset_items)) != len(subset_items):  # check for repetition in subset
        raise ValueError("Please input a pool with unique items")

    if (np.min(np.unique(pool_groups)) != 0) or (np.max(np.unique(pool_groups)) != len(np.unique(pool_groups))- 1): #check for consecutive group encoding in pool
        raise  ValueError("Please represent pool groups via consecutive integers")


# Function for error handling with group information
def check_subset_items_groups(pool_groups, subset_items, subset_groups):
    """
        Check whether input pool groups, subset, and protected attribute information is valid.

        Parameters
    ----------
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).

    Returns
    ----------
    Raise errors if found.
    """

    # error handling for types
    if not isinstance(pool_groups, np.ndarray):
        raise TypeError("Input pool_groups must be ndarray")

    if not isinstance(subset_items, np.ndarray):
        raise TypeError("Input subset_items must be ndarray")

    if not isinstance(subset_groups, np.ndarray):
        raise TypeError("Input subset_groups must be ndarray")

    # error handling for inputs sizes and values
    if len(subset_items) <= 0:  # check size of subset
        raise ValueError("Please input a valid subset")

    if len(subset_items) != len(subset_groups):  # check size of input subset and groups match
        raise ValueError("Please input a subset and groups of same size")

    if len(set(subset_items)) != len(subset_items):  # check for repetition in subset
        raise ValueError("Please input a pool with unique items")

    if (np.min(np.unique(pool_groups)) != 0) or (np.max(np.unique(pool_groups)) != len(
            np.unique(pool_groups)) - 1):  # check for consecutive group encoding in pool
        raise ValueError("Please represent pool groups via consecutive integers")


# Function for error handling with group information
def check_subset_groups(subset_items, subset_groups):
    """
        Check whether input subset, and protected attribute information is valid.

        Parameters
    ----------
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).

    Returns
    ----------
    Raise errors if found.
    """

    # error handling for types
    if not isinstance(subset_items, np.ndarray):
        raise TypeError("Input subset_items must be ndarray")

    if not isinstance(subset_groups, np.ndarray):
        raise TypeError("Input subset_groups must be ndarray")

    # error handling for inputs sizes and values
    if len(subset_items) <= 0:  # check size of subset
        raise ValueError("Please input a valid subset")

    if len(subset_items) != len(subset_groups):  # check size of input subset and groups match
        raise ValueError("Please input a subset and groups of same size")

    if len(set(subset_items)) != len(subset_items):  # check for repetition in subset
        raise ValueError("Please input a pool with unique items")

# function to audit for balance fairness
def balance(pool_groups, subset_items, subset_groups):
    """Compute the balance fairness metric.
    Parameters
    ----------
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    Returns
    ----------
    propOfS: numpy array of shape = (n_groups)
        Each group's proportion of the subset.
    bal_val: float
        The balance emetric value.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([1,4])
    >>> subset_scores = np.asarray([100,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> balance(pool_groups, subset_items, subset_groups)
    [0.5 0.5] 0.0
    """

    check_subset_items_groups(pool_groups, subset_items, subset_groups) # error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    propOfS  = np.full((num_unique_grps,), -np.Inf)
    total_items_subset = subset_items.shape[0]
    for grp in unique_grps:
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        propOfS[grp] = num_grp_items_in_subset /total_items_subset

    min_group_proportion_subset  = np.min(propOfS)
    max_group_proportion_subset = np.max(propOfS)
    bal_val =  min_group_proportion_subset / max_group_proportion_subset



    return propOfS, bal_val



def calibrated_parity(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, lb_bin, ub_bin):
    """Compute the calibrated parity.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    lb_bin: numpy array of shape = (n_bins)
        The lower bound scores for each bin (bin is greater than or equal to lower bound).
    ub_bin: numpy array of shape = (n_bins)
        The upper bound scores for each bin (bin is less than upper bound).
    Returns
    ----------
    bin_group_selection_proportions: numpy array of shape = (n_bins,n_groups)
        The proportion of each group selected into the subset from the bin
    dp_val: float
        Calibrated parity value.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([1,4])
    >>> subset_scores = np.asarray([100,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> lb_bin = np.asarray([0, 50])
    >>> ub_bin = np.asarray([49, 100])

    >>> calibrated_parity(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, lb_bin, ub_bin)
    (array([[0. , 1. ],
       [0.5, 0. ]]), array([0., 0.]), 0.0)
    """

    check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups) #error handling
    n_bins = lb_bin.shape[0]
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    bin_group_selectr = np.full((n_bins, num_unique_grps), -np.Inf)

    for bin_i in range(0,n_bins):
        lb = lb_bin[bin_i]
        ub = ub_bin[bin_i]
        greaterthanequal_lb_pool = pool_scores > lb
        lessthan_ub_pool = pool_scores <= ub
        bin_mask_pool = np.bitwise_and(greaterthanequal_lb_pool,lessthan_ub_pool)
        greaterthanequal_lb_subset = subset_scores > lb
        lessthan_ub_subset = subset_scores <= ub
        bin_mask_subset = np.bitwise_and(greaterthanequal_lb_subset, lessthan_ub_subset)
        bin_pool_items = pool_items[bin_mask_pool]
        bin_pool_groups = pool_groups[bin_mask_pool]
        bin_subset_items = subset_items[bin_mask_subset]
        bin_subset_groups = subset_groups[bin_mask_subset]
        for grp in unique_grps:
            grp_bin_pool_mask = bin_pool_groups == grp
            grp_bin_pool_items = bin_pool_items[grp_bin_pool_mask]
            num_grp_bin_pool_items = np.count_nonzero(grp_bin_pool_items)
            grp_bin_subset_mask = bin_subset_groups == grp
            grp_bin_subset_items = bin_subset_items[grp_bin_subset_mask]
            num_grp_bin_subset_items = np.count_nonzero(grp_bin_subset_items)
            if num_grp_bin_pool_items == 0:
                bin_group_selectr[bin_i, grp] = 0.0
            else:
                bin_group_selectr[bin_i, grp] = num_grp_bin_subset_items / num_grp_bin_pool_items

    max_prop_each_bin = np.max(bin_group_selectr, axis = 1)
    min_prop_each_bin = np.min(bin_group_selectr, axis = 1)


    if np.all(min_prop_each_bin == max_prop_each_bin):
        cp_val = 1 #totally fair since max = min in all bins
    else:
        different_bin_selection_rates_mask = min_prop_each_bin != max_prop_each_bin
        cp_val = np.min(min_prop_each_bin[different_bin_selection_rates_mask] / max_prop_each_bin[different_bin_selection_rates_mask])
    return bin_group_selectr, cp_val


def calibrated_balance(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, lb_bin, ub_bin):
    """Compute the calibrated balance.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    lb_bin: numpy array of shape = (n_bins)
        The lower bound scores for each bin (bin is greater than or equal to lower bound).
    ub_bin: numpy array of shape = (n_bins)
        The upper bound scores for each bin (bin is less than upper bound).
    Returns
    ----------
    bin_group_proportions: numpy array of shape = (n_bins,n_groups)
        The proportion of each group selected into the subset from the bin
    db_val: float
        Distributed parity value.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([2,4])
    >>> subset_scores = np.asarray([85,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> lb_bin = np.asarray([0, 87])
    >>> ub_bin = np.asarray([86, 100])

    >>> calibrated_balance(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, lb_bin, ub_bin)
    (array([[0.5, 0.5],
       [0. , 0. ]]), 1)
    """
    check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores,
                                 subset_groups)  # error handling
    n_bins = lb_bin.shape[0]
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    bin_group_proportions = np.full((n_bins, num_unique_grps), -np.Inf)

    for bin_i in range(0,n_bins):
        lb = lb_bin[bin_i]
        ub = ub_bin[bin_i]
        greaterthanequal_lb_pool = pool_scores > lb
        lessthan_ub_pool = pool_scores <= ub
        bin_mask_pool = np.bitwise_and(greaterthanequal_lb_pool,lessthan_ub_pool)
        greaterthanequal_lb_subset = subset_scores > lb
        lessthan_ub_subset = subset_scores <= ub
        bin_mask_subset = np.bitwise_and(greaterthanequal_lb_subset, lessthan_ub_subset)
        bin_pool_items = pool_items[bin_mask_pool]
        bin_pool_groups = pool_groups[bin_mask_pool]
        bin_subset_items = subset_items[bin_mask_subset]
        bin_subset_groups = subset_groups[bin_mask_subset]
        for grp in unique_grps:
            grp_bin_pool_mask = bin_pool_groups == grp
            grp_bin_pool_items = bin_pool_items[grp_bin_pool_mask]
            num_grp_bin_pool_items = np.count_nonzero(grp_bin_pool_items)
            grp_bin_subset_mask = bin_subset_groups == grp
            grp_bin_subset_items = bin_subset_items[grp_bin_subset_mask]
            num_grp_bin_subset_items = np.count_nonzero(grp_bin_subset_items)
            num_subset_items = np.count_nonzero(subset_items)
            if num_grp_bin_pool_items == 0:
                bin_group_proportions[bin_i, grp] = 0.0
            else:
                bin_group_proportions[bin_i, grp] = num_grp_bin_subset_items / num_subset_items

    max_props_each_bin = np.max(bin_group_proportions, axis = 1)
    min_props_each_bin = np.min(bin_group_proportions, axis = 1)




    if np.all(min_props_each_bin == max_props_each_bin):
        cb_val = 1 #totally fair since max = min in all bins
    else:
        different_bin_selection_rates_mask = min_props_each_bin != max_props_each_bin
        cb_val = np.min(min_props_each_bin[different_bin_selection_rates_mask] / max_props_each_bin[different_bin_selection_rates_mask])
    return bin_group_proportions, cb_val



def cond_parity(pool_items, pool_groups, pool_attribute, subset_items, subset_groups, subset_attribute, cond_val):
    """Compute conditioned parity.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    pool_attribute: numpy array of shape = (n_items)
        The additional attribute of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    subset_attribute: numpy array of shape = (n_items)
        The additional attribute of the items in the subset (corresponding to order of items in subset_items).
    cond_val: value to condition on
    Returns
    ----------
    CselectRt: numpy array of shape = (n_groups)
        The proportion of each conditioned group selected into the subset
    csp_val: float
        Conditioned Statistical Parity fairness.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> pool_attribute = np.asarray([0, 1, 0, 1])
    >>> subset_items = np.asarray([1,4])
    >>> subset_groups = np.asarray([0, 1])
    >>> subset_attribute = np.asarray([0, 1])
    >>> csp_val = 1
    >>> cond_parity(pool_items, pool_groups, pool_attribute, subset_items, subset_groups, subset_attribute, cond_val)
    array([0., 1.]), 0.0
    """

    check_pool_subset_items_groups(pool_items, pool_groups, subset_items, subset_groups) #error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    CselectRt  = np.full((num_unique_grps,), -np.Inf)
    #narrow the pool
    cond_pool_mask = pool_attribute == cond_val
    pool_groups = pool_groups[cond_pool_mask]
    #narrow the subset
    cond_subset_mask = subset_attribute == cond_val
    subset_groups = subset_groups[cond_subset_mask]
    for grp in unique_grps:
        pool_mask = pool_groups == grp
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        num_grp_items_in_pool = np.count_nonzero(pool_mask)
        CselectRt[grp] = num_grp_items_in_subset /num_grp_items_in_pool

    min_group_selection_prop  = np.min(CselectRt)
    max_group_selection_prop = np.max(CselectRt)
    csp_val = min_group_selection_prop / max_group_selection_prop
    return CselectRt, csp_val

def cond_balance(pool_groups, subset_items, subset_groups, subset_attribute, cond_val):
    """Compute the conditioned balance.
    Parameters
    ----------
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    subset_attribute: numpy array of shape = (n_items)
        The additional attribute of the items in the subset (corresponding to order of items in subset_items).
    cond_val: value to condition on
    Returns
    ----------
    CpropOfS: numpy array of shape = (n_groups)
        The proportion of the subset each group is
    cbal_val: float
        The balance error
    Examples
    --------
    --------
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([1,4])
    >>> subset_groups = np.asarray([0, 1])
    >>> subset_attribute = np.asarray([1, 1])
    >>> cond_val = 1
    >>> cond_balance(pool_groups, subset_items, subset_groups, subset_attribute, cond_val)
    [0.5 0.5] 0.0
    """

    check_subset_items_groups(pool_groups, subset_items, subset_groups)  # error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    CpropOfS  = np.full((num_unique_grps,), -np.Inf)

    # narrow the subset
    cond_subset_mask = subset_attribute == cond_val
    subset_items = subset_items[cond_subset_mask]
    subset_groups = subset_groups[cond_subset_mask]
    total_items_subset = subset_items.shape[0]
    for grp in unique_grps:
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        CpropOfS[grp] = num_grp_items_in_subset /total_items_subset

    min_group_proportion_subset  = np.min(CpropOfS)
    max_group_proportion_subset = np.max(CpropOfS)
    cbal_val =  min_group_proportion_subset / max_group_proportion_subset



    return CpropOfS, cbal_val



def qualififed_parity(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, q):
    """Compute qualified parity.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    q: float
        The relevance score for which items in the pool that have score >= q are "relevant".
    Returns
    ----------
    QselectRt: numpy array of shape = (n_groups)
        The proportion of each group selected into the subset from the qualified pool
    qp_val: float
        fairness.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([2,4])
    >>> subset_scores = np.asarray([85,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> q = 50

array([0.5, 0. ]), 0.0
    """

    check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores,
                                 subset_groups)  # error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    QselectRt  = np.full((num_unique_grps,), -np.Inf)
    qualified_mask = pool_scores >= q
    qualified_pool_groups =  pool_groups[qualified_mask]
    subset_qualified_mask = subset_scores >= q
    qualified_subset_groups = subset_groups[subset_qualified_mask]
    for grp in unique_grps:
        pool_mask = qualified_pool_groups == grp
        subset_mask = qualified_subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        num_grp_items_in_pool = np.count_nonzero(pool_mask)
        if num_grp_items_in_pool == 0:
            QselectRt[grp] = 0.0
        else:
            QselectRt[grp] = num_grp_items_in_subset /num_grp_items_in_pool

    min_group_selection_prop  = np.min(QselectRt)
    max_group_selection_prop = np.max(QselectRt)
    qp_val =  min_group_selection_prop / max_group_selection_prop



    return QselectRt, qp_val


def qualified_balance(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups, q):
    """Compute qualified balance.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    q: float
        The relevance score for which items in the pool that have score >= q are "relevant".
    Returns
    ----------
    QpropOfS: numpy array of shape = (n_groups)
        The proportion of each group selected into the subset from the qualified pool
    qb_val: float
        qualified balance fairness.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([2,4])
    >>> subset_scores = np.asarray([85,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> q = 50

array([0.5, 0. ]), 0.0
    """
    check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores,
                                 subset_groups)  # error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    QpropOfS  = np.full((num_unique_grps,), -np.Inf)
    qualified_mask = pool_scores >= q
    qualified_pool_groups =  pool_groups[qualified_mask]
    subset_qualified_mask = subset_scores >= q
    qualified_subset_groups = subset_groups[subset_qualified_mask]
    total_items_subset = subset_items.shape[0]
    for grp in unique_grps:
        pool_mask = qualified_pool_groups == grp
        subset_mask = qualified_subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        num_grp_items_in_pool = np.count_nonzero(pool_mask)
        if num_grp_items_in_pool == 0:
            QpropOfS[grp] = 0.0
        else:
            QpropOfS[grp] = num_grp_items_in_subset /total_items_subset

    min_group_selection_prop  = np.min(QpropOfS)
    max_group_selection_prop = np.max(QpropOfS)
    qb_val =  min_group_selection_prop / max_group_selection_prop



    return QpropOfS, qb_val

def relevance_parity(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups):
    """Compute the relevance parity.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_scores: numpy array of shape = (n_items)
        The scores of the items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    Returns
    ----------
    RselectRt: numpy array of shape = (n_groups)
        The relevance select rate
    rp_val: float
        Statistical Parity fairness.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> pool_scores = np.asarray([100, 85, 54, 12])
    >>> subset_items = np.asarray([1,4])
    >>> subset_groups = np.asarray([0, 1])
    >>> subset_scores = np.asarray([100,12])
    >>> relevance_parity(pool_items, pool_scores, pool_groups, subset_items, subset_scores, subset_groups)
    array([0.01081081, 0.03030303]), 0.3567567567567568
    """


    check_pool_subset_groups(pool_items, pool_scores, pool_groups, subset_items, subset_scores,
                                 subset_groups)  # error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    RselectRt  = np.full((num_unique_grps,), -np.Inf)
    for grp in unique_grps:
        pool_mask = pool_groups == grp
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        num_grp_items_in_pool = np.count_nonzero(pool_mask)
        sum_scores_grp_in_pool = np.sum(pool_scores[pool_mask])
        avg_grp_score = sum_scores_grp_in_pool/ num_grp_items_in_pool
        RselectRt[grp] = num_grp_items_in_subset / avg_grp_score

    min_group_selection_prop  = np.min(RselectRt)
    max_group_selection_prop = np.max(RselectRt)
    rp_val = min_group_selection_prop / max_group_selection_prop
    return RselectRt, rp_val

def score_parity(subset_items, subset_scores, subset_groups):
    """Compute score parity.
    Parameters
    ----------
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    q: float
        The relevance score for which items in the pool that have score >= q are "relevant".
    Returns
    ----------
    AvgScore: numpy array of shape = (n_groups)
        The average score of a group
    sp_val: float
        fairness.
    Examples
    --------
    --------
    >>> subset_items = np.asarray([2,4])
    >>> subset_scores = np.asarray([85,12])
    >>> subset_groups = np.asarray([0, 1])
    >>> print(score_parity(subset_items, subset_scores, subset_groups))
    array([85., 12.]), 0.1411764705882353
    """

    unique_grps = np.unique(subset_groups)
    AvgScore = []
    for grp in unique_grps:
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        total_grp_score = np.sum(subset_scores[subset_mask])
        AvgScore.append(total_grp_score / num_grp_items_in_subset)

    min_group_selection_prop = np.min(AvgScore)
    max_group_selection_prop = np.max(AvgScore)
    sp_val = min_group_selection_prop / max_group_selection_prop
    AvgScore = np.asarray(AvgScore)
    return AvgScore, sp_val


def score_balance(subset_items, subset_scores, subset_groups):
    """Compute score balance.
    Parameters
    ----------
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_scores : numpy array of shape = (n_items)
        The scores of the items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    q: float
        The relevance score for which items in the pool that have score >= q are "relevant".
    Returns
    ----------
    TotalScore: numpy array of shape = (n_groups)
        The average score of a group
    sp_val: float
        fairness.
    Examples
    --------
    --------
    >>> subset_items = np.asarray([2,4, 3])
    >>> subset_scores = np.asarray([85,12, 54])
    >>> subset_groups = np.asarray([0, 1, 1])
    >>> print(score_balance(subset_items, subset_scores, subset_groups))
array([85., 66.]), 0.7764705882352941
    """

    unique_grps = np.unique(subset_groups)
    TotalScore = []
    for grp in unique_grps:
        subset_mask = subset_groups == grp
        total_grp_score = np.sum(subset_scores[subset_mask])
        TotalScore.append(total_grp_score)

    min_group_selection_prop = np.min(TotalScore)
    max_group_selection_prop = np.max(TotalScore)
    sb_val = min_group_selection_prop / max_group_selection_prop
    TotalScore = np.asarray(TotalScore)
    return TotalScore, sb_val


def parity(pool_items, pool_groups, subset_items, subset_groups):
    """Compute the error in selection statistical parity.
    Parameters
    ----------
    pool_items : numpy array of shape = (n_items)
        The items in the pool (sorted by relevance score).
    pool_groups: numpy array of shape = (n_items)
        The group identity of the items in the pool (corresponding to order of items in pool_items).
    subset_items : numpy array of shape = (n_items)
        The items in the subset(sorted by relevance score).
    subset_groups: numpy array of shape = (n_items)
        The group identity of the items in the subset (corresponding to order of items in subset_items).
    Returns
    ----------
    selectRt: numpy array of shape = (n_groups)
        The proportion of each group selected into the subset
    sp_val: float
        Parity fairness.
    Examples
    --------
    --------
    >>> pool_items = np.asarray([1,2,3,4])
    >>> pool_groups = np.asarray([0, 0, 1, 1])
    >>> subset_items = np.asarray([1,4])
    >>> subset_groups = np.asarray([0, 1])
    >>> parity(pool_items, pool_groups, subset_items, subset_groups)
    [0.5 0.5] 1.0
    """

    check_pool_subset_items_groups(pool_items, pool_groups, subset_items, subset_groups) #error handling
    unique_grps = np.unique(pool_groups)
    num_unique_grps = unique_grps.shape[0]
    selectRt  = np.full((num_unique_grps,), -np.Inf)
    for grp in unique_grps:
        pool_mask = pool_groups == grp
        subset_mask = subset_groups == grp
        num_grp_items_in_subset = np.count_nonzero(subset_mask)
        num_grp_items_in_pool = np.count_nonzero(pool_mask)
        selectRt[grp] = num_grp_items_in_subset /num_grp_items_in_pool

    min_group_selection_prop  = np.min(selectRt)
    max_group_selection_prop = np.max(selectRt)
    sp_val = min_group_selection_prop / max_group_selection_prop
    return selectRt, sp_val