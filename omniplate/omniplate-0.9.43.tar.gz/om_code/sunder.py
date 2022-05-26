# functions for taking subsets of the data
import numpy as np
import om_code.omgenutils as gu
import om_code.omerrors as errors


def getsubset(
    inst,
    type,
    set="all",
    includes=False,
    excludes=False,
    nonull=False,
    nomedia=False,
):
    """
    Returns a subset of either the conditions or strains.

    Parameters
    --
    inst: instance of platereader
    type: string
        Either 'c' (conditions) or 's' (strains).
    set: list of strings
        List of items to include (default is 'all').
    includes: string
        Select only items with this string in their name.
    excludes: string
        Ignore any items with this string in their name.
    nonull: boolean
        If True, ignore Null strain.
    nomedia: boolean
        If True, ignores 'media' condition.

    Returns
    -------
    sset: list of strings
    """
    if set == "all" or includes or excludes:
        if type == "c":
            sset = list(
                np.unique(
                    [
                        con
                        for e in inst.allconditions
                        for con in inst.allconditions[e]
                    ]
                )
            )
            if nomedia and "media" in sset:
                sset.pop(sset.index("media"))
        elif type == "s":
            sset = list(
                np.unique(
                    [
                        str
                        for e in inst.allstrains
                        for str in inst.allstrains[e]
                    ]
                )
            )
            if nonull and "Null" in sset:
                sset.pop(sset.index("Null"))
        else:
            sset = inst.allexperiments
        # find those items containing keywords given in 'includes'
        if includes:
            includes = gu.makelist(includes)
            newset = []
            for s in sset:
                gotone = 0
                for item in includes:
                    if item in s:
                        gotone += 1
                if gotone == len(includes):
                    newset.append(s)
            sset = newset
        # remove any items containing keywords given in 'excludes'
        if excludes:
            excludes = gu.makelist(excludes)
            exs = []
            for s in sset:
                for item in excludes:
                    if item in s:
                        exs.append(s)
                        break
            for ex in exs:
                sset.pop(sset.index(ex))
    else:
        sset = gu.makelist(set)
    if sset:
        # sort by numeric values in list entries
        return sorted(sset, key=gu.natural_keys)
    else:
        if includes:
            raise errors.getsubset(
                "Nothing found for " + " and ".join(includes)
            )
        else:
            raise errors.getsubset("Nothing found")


###


def getexps(inst, experiments, experimentincludes, experimentexcludes):
    """
    Returns list of experiments
    """
    if experimentincludes or experimentexcludes:
        exps = getsubset(
            inst,
            "e",
            includes=experimentincludes,
            excludes=experimentexcludes,
        )
    elif experiments == "all":
        exps = inst.allexperiments
    else:
        exps = gu.makelist(experiments)
    return exps


###


def getcons(inst, conditions, conditionincludes, conditionexcludes, nomedia):
    """
    Returns list of conditions
    """
    if conditionincludes or conditionexcludes:
        cons = getsubset(
            inst,
            "c",
            includes=conditionincludes,
            excludes=conditionexcludes,
            nomedia=nomedia,
        )
    elif conditions == "all":
        cons = list(
            np.unique(
                [
                    con
                    for e in inst.allconditions
                    for con in inst.allconditions[e]
                ]
            )
        )
        if nomedia and "media" in cons:
            cons.pop(cons.index("media"))
    else:
        cons = gu.makelist(conditions)
    return sorted(cons, key=gu.natural_keys)


###


def getstrs(inst, strains, strainincludes, strainexcludes, nonull):
    """
    Returns list of strains
    """
    if strainincludes or strainexcludes:
        strs = getsubset(
            inst,
            "s",
            includes=strainincludes,
            excludes=strainexcludes,
            nonull=nonull,
        )
    elif strains == "all":
        strs = list(
            np.unique(
                [str for e in inst.allstrains for str in inst.allstrains[e]]
            )
        )
        if nonull and "Null" in strs:
            strs.pop(strs.index("Null"))
    else:
        strs = gu.makelist(strains)
    if nonull and "Null" in strs:
        strs.pop(strs.index("Null"))
    return sorted(strs, key=gu.natural_keys)


###


def getall(
    inst,
    experiments,
    experimentincludes,
    experimentexcludes,
    conditions,
    conditionincludes,
    conditionexcludes,
    strains,
    strainincludes,
    strainexcludes,
    nonull=True,
    nomedia=True,
):
    """
    Returns experiments, conditions, and strains
    """
    exps = getexps(inst, experiments, experimentincludes, experimentexcludes)
    cons = getcons(
        inst, conditions, conditionincludes, conditionexcludes, nomedia
    )
    strs = getstrs(inst, strains, strainincludes, strainexcludes, nonull)
    return exps, cons, strs


###


def extractwells(r_df, s_df, experiment, condition, strain, datatypes):
    """
    Extracts a list of matrices for each dtype in
    datatypes for the given experiment, condition, and strain with each
    column in each matrix having the data for one well
    """
    datatypes = gu.makelist(datatypes)
    # restrict time if necessary
    lrdf = r_df[
        (r_df.time >= s_df.time.min()) & (r_df.time <= s_df.time.max())
    ]
    # extract data
    df = lrdf.query(
        "experiment == @experiment and condition == @condition "
        "and strain == @strain"
    )
    matrices = []
    for dtype in datatypes:
        df2 = df[[dtype, "well"]]
        df2well = df2.groupby("well")[dtype].apply(list)
        matrices.append(np.transpose([df2well[w] for w in df2well.index]))
    if len(datatypes) == 1:
        # return array
        return matrices[0]
    else:
        # return list of arrays
        return matrices
