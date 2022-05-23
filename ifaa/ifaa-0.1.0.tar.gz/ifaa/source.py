#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 21:26:38 2022

@author: ss
"""
import joblib
import contextlib
import math
import timeit
import scipy
import warnings
import numpy as np
import pandas as pd
import multiprocessing as mp
import glmnet_python
from joblib import Parallel, delayed
from tqdm import tqdm
from functools import partial
from cvglmnet import cvglmnet
from cvglmnetCoef import cvglmnetCoef
from glmnet import glmnet
from glmnetCoef import glmnetCoef
from statsmodels.api import OLS


def IFAA(
    MicrobData,
    CovData,
    linkIDname,
    testCov=[],
    ctrlCov=[],
    testMany=True,
    ctrlMany=False,
    nRef=40,
    nRefMaxForEsti=2,
    refTaxa=[],
    adjust_method="fdr_by",
    fdrRate=0.15,
    paraJobs=[],
    bootB=500,
    standardize=False,
    sequentialRun=False,
    refReadsThresh=0.2,
    taxDropThresh=0,
    SDThresh=0.05,
    SDquantilThresh=0,
    balanceCut=0.2,
    seed=1,
):
    """
    Robust association identification and inference for absolute abundance in microbiome analyses

    Make inference on the association of microbiome with covariates. Most of the time, users just need to feed the first five inputs to the function: MicrobData, CovData, linkIDname, testCov and ctrlCov. All other inputs can just take their default values.

    ARGUMENTS:
    ---------------
    MicrobData : pandas DataFrame
        Microbiome data matrix containing microbiome absolute abundance or relative abundance with each row per sample and each column per taxon/OTU/ASV (or any other unit). It should contain an id variable to be linked with the id variable in the covariates data: CovData.
    CovData : pandas DataFrame
        Covariates data matrix containing covariates and confounders with each row per sample and each column per variable. Any categorical variable should be converted into dummy variables in this data matrix unless it can be treated as a continuous variable. It should also contain an id variable to be linked with the id variable in the microbiome data: MicrobData. 
    linkIDname : str
        The common variable name of the id variable in both MicrobData and CovData. The two data sets will be merged by this id variable.
    testCov : list of str
        Covariates that are of primary interest for testing and estimating the associations. It corresponds to :math:`X_i` in the equation. Default is NULL which means all covariates are testCov.
    ctrlCov : list of str
        Potential confounders that will be adjusted in the model. It corresponds to :math:`W_i` in the equation. Default is NULL which means all covariates except those in testCov are adjusted as confounders.
    testMany : boolean
        This takes logical value True or False. If True, the testCov will contain all the variables in CovData provided testCov is set to be NULL. The default value is True which does not do anything if testCov is not NULL.
    ctrlMany : boolean
        This takes logical value True or False. If True, all variables except testCov are considered as control covariates provided ctrlCov is set to be NULL. The default value is False.
    nRef : int
           The number of randomly picked reference taxa used in phase 1. Default number is 40.
    nRefMaxForEsti : int
        The maximum number of final reference taxa used in phase 2. The default is 2.
    refTaxa : list of str
        A vector of taxa or OTU or ASV names. These are reference taxa specified by the user to be used in phase 1. If the number of reference taxa is less than 'nRef', the algorithm will randomly pick extra reference taxa to make up 'nRef'. The default is NULL since the algorithm will pick reference taxa randomly.
    adjust_method : str
        The adjusting method for p value adjustment. Default is "fdr_by" for dependent FDR adjustment. It can take other adjustment method available in statsmodels.
    fdrRate : float
        The false discovery rate for identifying taxa/OTU/ASV associated with testCov. Default is 0.15.
    paraJobs : int  
        If sequentialRun is False, this specifies the number of parallel jobs that will be registered to run the algorithm. If specified as NULL, it will automatically detect the cores to decide the number of parallel jobs. Default is NULL.
    bootB : int
        Number of bootstrap samples for obtaining confidence interval of estimates in phase 2 for the high dimensional regression. The default is 500.
    standardize : boolean 
        This takes a logical value True or False. If True, the design matrix for :math:`X` will be standardized in the analyses and the results. Default is False.
    sequentialRun : boolean
        This takes a logical value True or False. Default is False. This argument could be useful for debug.
    refReadsThresh : float
        The threshold of proportion of non-zero sequencing reads for choosing the reference taxon in phase 2. The default is 0.2 which means at least 20% non-zero sequencing reads.
    taxDropThresh : float
        The threshold of number of non-zero sequencing reads for each taxon to be dropped from the analysis. The default is 0 which means taxon without any sequencing reads will be dropped from the analysis.
    SDThresh : float    
        The threshold of standard deviations of sequencing reads for been chosen as the reference taxon in phase 2. The default is 0.05 which means the standard deviation of sequencing reads should be at least 0.05 in order to be chosen as reference taxon.
    SDquantilThresh : float
        The threshold of the quantile of standard deviation of sequencing reads, above which could be selected as reference taxon. The default is 0.
    balanceCut : float 
        The threshold of the proportion of non-zero sequencing reads in each group of a binary variable for choosing the final reference taxa in phase 2. The default number is 0.2 which means at least 20% non-zero sequencing reads in each group are needed to be eligible for being chosen as a final reference taxon.
    seed : int
           Random seed for reproducibility. Default is 1. It can be set to be NULL to remove seeding.

    OUTPUT : 
    ----------------

    sig_results :    dict 
        containing estimating results that are statistically significant.
    full_results :   dict 
        containing all estimating results. NA denotes unestimable.
    covariatesData : pandas DataFrame
        containing covariates and confounders used in the analyses.
    Please use *.keys() to see other output components

    EXAMPLES:
    --------
    >>> import numpy as np
    >>> from loadData import *

    >>> res = IFAA(load_dataM().iloc[:,:], 
    ...            load_dataC().iloc[:,:], 
    ...            testCov = ['v1'],
    ...            ctrlCov = ['v2', 'v3'],
    ...            paraJobs = 4,
    ...            linkIDname="id",
    ...            refTaxa = ["rawCount" + str(i + 1) for i in range(40)],
    ...            bootB = 100,
    ...            sequentialRun=False)

    >>> res['sig_results']
    >>> res['full_results']
    >>> res['analysisResults']['finalizedBootRefTaxon']
    >>> res['covriateNames']

    DETAILS:
    -------
        To model the association, the following equation is used:

                        .. math:: \log(\mathcal{Y}_i^k)|\mathcal{Y}_i^k>0 =\\beta ^{0k}+X_i^T \\beta ^k+W_i^T\gamma^k+Z_i^Tb_i+\epsilon_i^k; \hspace{0.5cm}k=1,...,K+1 
            where
                :math:`Y_i^k` is the AA of taxa k in subject i in the entire ecosystem.

                :math:`X_i` is the covariate matrix.

                :math:`W_i` is the confounder matrix.

                :math:`Z_i` is the design matrix for random effects.

                :math:`\\beta^k` is the regression coefficients that will be estimated and tested with the IFAA() function.

        The challenge in microbiome analysis is that :math:`Y_i^k` can not be observed. What is observed is its small proportion:

                        .. math:: Y_i^k=C_iY^k_i, 

            where 
                :math:`C_i` is an unknown number between 0 and 1 that denote the observed proportion.

        The IFAA method can successfully addressed this challenge. The IFAA() will estimate the parameter :math:`\\beta^k` and their 95% confidence intervals. High-dimensional :math:`X_i` is handled by regularization.

    AUTHORS:
    -------
        Shangchen Song (Python)
        
        Zhigang Li, Quran Wu (Theroy and R)

    REFERENCES:
    ---------- 
        Li et al.(2021) IFAA: Robust association identification and Inference For Absolute Abundance in microbiome analyses. 
        Journal of the American Statistical Association

        Zhang CH (2010) Nearly unbiased variable selection under minimax concave penalty. 
        Annals of Statistics. 38(2):894-942.

        Liu et al.(2020) A bootstrap lasso + partial ridge method to construct confidence intervals for parameters in high-dimensional sparse linear models. 
        Statistica Sinica

    SEE ALSO:
    --------
        IFAA's R version on CRAN 

        https://cran.r-project.org/package=IFAA

    """
    # Make arguments as numpy arries
    testCov = np.array(testCov)
    ctrlCov = np.array(ctrlCov)
    linkIDname = np.array(linkIDname)
    refTaxa = np.array(refTaxa)
    paraJobs = np.array([paraJobs])

    # results container, a dictionary
    results = {}
    if seed is not None:
        np.random.seed(seed)
        scipy.random.seed(seed)
    start_time = timeit.default_timer()

    runMeta = metaData(
        MicrobData=MicrobData,
        CovData=CovData,
        linkIDname=linkIDname,
        taxDropThresh=taxDropThresh,
        standardize=standardize,
        testCov=testCov,
        ctrlCov=ctrlCov,
        testMany=testMany,
        ctrlMany=ctrlMany,
    )

    data = runMeta["data"]
    results["covariatesData"] = runMeta["covariatesData"]
    binaryInd = runMeta["binaryInd"]
    covsPrefix = runMeta["covsPrefix"]
    Mprefix = runMeta["Mprefix"]
    testCovInd = runMeta["testCovInd"]
    testCovInOrder = runMeta["testCovInOrder"]
    testCovInNewNam = runMeta["testCovInNewNam"]
    ctrlCov = runMeta["ctrlCov"]
    microbName = runMeta["microbName"]
    newMicrobNames = runMeta["newMicrobNames"]
    results["covriateNames"] = runMeta["xNames"]
    binaryInd_test = testCovInd[r_in(testCovInd, binaryInd)]
    del runMeta

    if len(refTaxa) > 0:
        if sum(r_in(refTaxa, microbName)) != len(refTaxa):
            raise Exception(
                """
                             Error: One or more of the specified reference taxa in phase 1 have no sequencing reads 
                             or are not in the data set. Double check the names of the reference taxa and their 
                             sparsity levels."""
            )
    if nRefMaxForEsti < 2:
        nRefMaxForEsti = 2
        warnings.warn(
            "Warning: Needs at least two final reference taxon for estimation."
        )

    if nRef > len(microbName):
        raise Exception(
            "Error: number of random reference taxa can not be larger than the total number of taxa in the data. Try lower nRef"
        )

    refTaxa_newNam = newMicrobNames[r_in(microbName, refTaxa)]

    results["analysisResults"] = Regulariz(
        data=data,
        testCovInd=testCovInd,
        testCovInOrder=testCovInOrder,
        testCovInNewNam=testCovInNewNam,
        microbName=microbName,
        nRef=nRef,
        nRefMaxForEsti=nRefMaxForEsti,
        binaryInd=binaryInd,
        binaryInd_test=binaryInd_test,
        covsPrefix=covsPrefix,
        Mprefix=Mprefix,
        refTaxa=refTaxa_newNam,
        paraJobs=paraJobs,
        adjust_method=adjust_method,
        fwerRate=fdrRate,
        bootB=bootB,
        sequentialRun=sequentialRun,
        refReadsThresh=refReadsThresh,
        SDThresh=SDThresh,
        SDquantilThresh=SDquantilThresh,
        balanceCut=balanceCut,
        seed=seed,
    )

    rm(data)

    results["sig_results"] = results["analysisResults"]["sig_results"]
    results["full_results"] = results["analysisResults"]["full_results"]

    results["testCov"] = testCovInOrder
    results["ctrlCov"] = ctrlCov
    results["microbName"] = microbName
    results["bootB"] = bootB
    results["refReadsThresh"] = refReadsThresh
    results["balanceCut"] = balanceCut
    results["SDThresh"] = SDThresh
    results["paraJobs"] = paraJobs
    results["SDquantilThresh"] = SDquantilThresh
    results["nRef"] = nRef

    if isinstance(seed, int):
        results["seed"] = seed
    else:
        results["seed"] = "No seed used."

    totalTimeMins = (timeit.default_timer() - start_time) / 60
    print("The entire analysis took ", np.round(totalTimeMins, 2), " minutes")

    results["totalTimeMins"] = totalTimeMins

    return results


def metaData(
    MicrobData,
    CovData,
    linkIDname,
    taxDropThresh,
    standardize,
    testCov=np.empty(0),
    ctrlCov=np.empty(0),
    testMany=True,
    ctrlMany=True,
    MZILN=False,
):
    results = {}

    if not linkIDname:
        raise Exception("linkIDname is missing.")

    if len(testCov) > 0 and len(ctrlCov) > 0:
        if sum(r_in(np.concatenate((testCov, ctrlCov)), colnames(CovData))) != len(
            np.concatenate((testCov, ctrlCov))
        ):
            raise Exception("Error: some covariates are not available in the data.")

    if sum(r_in(testCov, ctrlCov)) > 0:
        warnings.warn(
            "Variables appeared in both testCov list and ctrlCov list will be treated as testCov."
        )

    # read microbiome data
    MdataWithId = MicrobData
    if len(colnames(MdataWithId)) != ncol(MdataWithId):
        raise Exception("Microbiome data lack variable names.")

    if (MdataWithId.loc[:, MdataWithId.columns != linkIDname].values < 0).any():
        raise Exception("Microbiome data contains negative values.")

    if MdataWithId[linkIDname].isna().mean() > 0.8:
        warnings.warn(
            "There are over 80% missing values for the linkId variable in the Microbiome data file. Double check the data format."
        )

    # read covariate data
    CovarWithId = CovData
    if CovarWithId[linkIDname].isna().mean() > 0.8:
        warnings.warn(
            "There are over 80% missing values for the linkId variable in the covariates data file. Double check the data format."
        )

    Covariates1 = CovarWithId.loc[:, CovarWithId.columns != linkIDname]

    # determine testCov and ctrlCov
    if len(testCov) == 0:
        if not testMany:
            raise Exception(
                "No covariates are specified for estimating associations of interest."
            )
        else:
            print(
                "Associations are being estimated for all covariates since no covariates are specified for testCov."
            )
            testCov = colnames(Covariates1)
    results["testCov"] = testCov

    xNames = colnames(Covariates1)
    rm(Covariates1)

    if len(ctrlCov) == 0 and ctrlMany:
        print(
            "No control covariates are specified, all variables except testCov are considered as control covariates."
        )
        ctrlCov = xNames[r_ni(xNames, testCov)]
    ctrlCov = ctrlCov[r_ni(ctrlCov, testCov)]
    results["ctrlCov"] = ctrlCov

    # merge data to remove missing
    CovarWithId1 = CovarWithId[np.hstack([linkIDname, testCov, ctrlCov])]
    allRawData = CovarWithId1.merge(MdataWithId, on=linkIDname.tolist()).dropna()
    CovarWithId = allRawData.loc[:, r_in(colnames(allRawData), colnames(CovarWithId1))]
    Covariates = CovarWithId.loc[:, r_ni(colnames(CovarWithId), [linkIDname])]
    rm(CovarWithId1)

    if not all(Covariates.apply(lambda a: a.dtype.kind in "if")):
        raise Exception(
            "There are non-numeric variables in the covariates for association test."
        )

    MdataWithId = allRawData.loc[:, r_in(colnames(allRawData), colnames(MdataWithId))]
    Mdata_raw = MdataWithId.loc[:, r_ni(colnames(MdataWithId), linkIDname)]
    rm(allRawData)

    # check zero taxa and subjects with zero taxa reads
    numTaxaNoReads = sum(colSums(Mdata_raw != 0) <= taxDropThresh)
    if numTaxaNoReads > 0:
        Mdata_raw = Mdata_raw.loc[:, colSums(Mdata_raw != 0) > taxDropThresh]
        print(
            "There are ",
            numTaxaNoReads,
            " taxa without any sequencing reads before data merging, and excluded from the analysis",
        )
    rm(numTaxaNoReads)

    numSubNoReads = sum(rowSums(Mdata_raw != 0) <= 1)
    if numSubNoReads > 0:
        print(
            "There are ",
            numSubNoReads,
            " subjects with zero or one sequencing read and excluded from the analysis",
        )
        subKeep = inv_bool(rowSums(Mdata_raw != 0) <= 1)
        Mdata_raw = Mdata_raw.loc[subKeep, :]
        MdataWithId = MdataWithId.loc[subKeep, :]
        rm(subKeep)
    rm(numSubNoReads)

    Mdata = Mdata_raw
    rm(Mdata_raw)

    microbName1 = colnames(Mdata)
    microbName = microbName1
    newMicrobNames1 = np.array(["microb" + str(i + 1) for i in range(len(microbName))])
    newMicrobNames = newMicrobNames1
    results["Mprefix"] = "microb"
    Mdata = Mdata.rename(columns=dict(zip(microbName1, newMicrobNames)))

    MdataWithId_new = cbind([MdataWithId.loc[:, linkIDname], Mdata])

    results["microbName"] = microbName
    results["newMicrobNames"] = newMicrobNames

    if Covariates.isna().sum().sum() > 0:
        print("Samples with missing covariate values are removed from the analysis.")

    if not Covariates[ctrlCov].apply(pd.api.types.is_numeric_dtype).all():
        warnings.warn("There are non-numeric variables in the control covariates")
        nonNumCols = which(
            ~Covariates[ctrlCov].apply(pd.api.types.is_numeric_dtype)
        )  # Negate boolean values by ~ in pandas
        for i in range(len(nonNumCols)):
            Covariates[ctrlCov[nonNumCols[i]]] = pd.factorize(
                Covariates[ctrlCov[nonNumCols[i]]]
            )[0]

    xNames = colnames(Covariates)
    nCov = len(xNames)

    binCheck = Covariates.nunique()

    if any(binCheck == 2):
        binaryInd = which(binCheck == 2)
        results["varNamForBin"] = xNames[binCheck == 2]
        results["nBinVars"] = len(results["varNamForBin"])

        # Convert binary variables into 0 and 1
        for i in range(results["nBinVars"]):
            iNam = results["varNamForBin"][i]
            mini = min(Covariates.loc[:, iNam])
            maxi = max(Covariates.loc[:, iNam])
            if any((mini != 0, maxi != 1)):
                Covariates.loc[Covariates.loc[:, iNam] == mini, iNam] = 0
                Covariates.loc[Covariates.loc[:, iNam] == maxi, iNam] = 1
                print(
                    "Binary covariate",
                    iNam,
                    "is not coded as 0/1 which may generate analysis bias. It has been changed to 0/1. The changed covariates data can be extracted from the result file.",
                )
    else:
        results["nBinVars"] = 0
        binaryInd = []
        results["varNamForBin"] = []

    results["binaryInd"] = binaryInd
    results["xNames"] = colnames(Covariates)

    if standardize:
        temp = Covariates.loc[:, Covariates.columns.difference(results["varNamForBin"])]
        Covariates.loc[:, Covariates.columns.difference(results["varNamForBin"])] = (
            temp / temp.std()
        )

    xNewNames = np.array(["x" + str(i + 1) for i in range(len(xNames))])
    Covariates = Covariates.rename(columns=dict(zip(colnames(Covariates), xNewNames)))
    results["covsPrefix"] = "x"
    results["xNewNames"] = xNewNames

    results["testCovInd"] = which(r_in(results["xNames"], testCov))

    results["testCovInOrder"] = results["xNames"][results["testCovInd"]]
    results["testCovInNewNam"] = results["xNewNames"][results["testCovInd"]]
    del (xNames, xNewNames)

    CovarWithId_new = cbind([CovarWithId.loc[:, linkIDname], Covariates])
    data = MdataWithId_new.merge(CovarWithId_new, on=linkIDname.tolist())
    dataOmit = data.dropna()

    results["covariatesData"] = CovarWithId_new
    results["covariatesData"].rename(
        columns=dict(
            zip(results["covariatesData"], np.insert(results["xNames"], 0, linkIDname))
        )
    )
    del (MdataWithId_new, CovarWithId_new)

    Mdata_omit = dataOmit.loc[:, np.array(newMicrobNames1)]

    # check taxa with zero or 1 read again after all missing data removed
    numTaxaNoReads = np.sum(colSums(Mdata_omit != 0) <= taxDropThresh)
    if numTaxaNoReads == 0:
        results["data"] = dataOmit

    if numTaxaNoReads > 0:
        dataOmit_noTaxa = dataOmit.loc[:, ~r_in(colnames(dataOmit), newMicrobNames1)]
        microbToRetain = newMicrobNames1[~(colSums(Mdata_omit != 0) <= taxDropThresh)]
        print(
            "There are ",
            numTaxaNoReads,
            " taxa without any sequencing reads after merging and removing all missing data, and excluded from the analysis",
        )

        MdataToRetain = Mdata_omit[microbToRetain]
        microbName = microbName1[r_in(newMicrobNames1, microbToRetain)]
        results["microbName"] = microbName
        newMicrobNames1 = ["microb" + str(i + 1) for i in range(len(microbName))]
        newMicrobNames = newMicrobNames1
        results["newMicrobNames"] = newMicrobNames
        MdataToRetain.columns = microbToRetain
        results["data"] = cbind((dataOmit_noTaxa, MdataToRetain))

    # output data summary
    print("Data dimensions (after removing missing data if any):")
    print(results["data"].shape[0], " samples")
    print(ncol(Mdata), " taxa/OTU/ASV")

    if not MZILN:
        print(len(results["testCovInOrder"]), " testCov variables in the analysis")
    if MZILN:
        print(len(results["testCovInOrder"]), " covariates in the analysis")

    if len(results["testCovInOrder"]) > 0:

        if not MZILN:
            print("These are the testCov variables:")
        if MZILN:
            print("These are the covariates:")

        print(*results["testCovInOrder"], sep=", ")

    if not MZILN:
        print(len(ctrlCov), " ctrlCov variables in the analysis ")
        if len(ctrlCov) > 0:
            print("These are the ctrlCov variables:")
            print(*ctrlCov, sep=", ")

    print(results["nBinVars"], " binary covariates in the analysis")

    if results["nBinVars"] > 0:
        print("These are the binary covariates:")
        print(results["varNamForBin"])

    return results


def dataInfo(
    data,
    Mprefix,
    covsPrefix,
    binPredInd,
    refReadsThresh=None,
    SDThresh=None,
    SDquantilThresh=None,
    balanceCut=None,
    qualifyRefTax=False,
):
    results = {}

    # get the original sample size
    nSub = nrow(data)
    MVarNamLength = len(Mprefix)

    # get taxa variable names
    microPositions = data.columns.str.startswith(Mprefix)
    nTaxa = len(which(microPositions))
    taxaNames = data.columns[microPositions]

    # to add if qualifyreftax
    if qualifyRefTax:
        qualifyData = data.loc[rowSums(data.loc[:, taxaNames] > 0) >= 2, :]
        w = qualifyData.loc[:, taxaNames]
        nSubQualif = nrow(qualifyData)
        taxaOverThresh = taxaNames[colSums(w > 0) >= (nSubQualif * refReadsThresh)]
        if len(taxaOverThresh) == 0:
            print(
                "There are no taxa with presence over the threshold:",
                refReadsThresh,
                ". Try lower the reference taxa reads threshold.",
                "\n",
            )

        # check the sd threshold
        sdTaxaOverThresh = np.zeros(len(taxaOverThresh))

        for i in range(len(taxaOverThresh)):
            taxa_i = w.loc[:, taxaOverThresh[i]].to_numpy()
            if np.sum(taxa_i > 0) > 1:
                sdTaxaOverThresh[i] = np.std(taxa_i[(taxa_i > 0)], ddof=1)

        results["sdTaxa"] = sdTaxaOverThresh

        TaxaOverSdThresh = taxaOverThresh[(sdTaxaOverThresh >= SDThresh)]
        if len(TaxaOverSdThresh) == 0:
            print(
                "There are no taxa with SD over the SD threshold:",
                SDThresh,
                ". Try lower the SD threshold",
                "\n",
            )
            rm(taxa_i, taxaOverThresh)

        # check the sd quantile threshold

        sdAllTaxa = np.zeros(nTaxa)
        for i in range(nTaxa):
            taxaAll_i = w.loc[:, taxaNames[i]]
            posTaxaAll_i = taxaAll_i[(taxaAll_i > 0)]
            if len(posTaxaAll_i) > 1:
                sdAllTaxa[i] = np.std(posTaxaAll_i, ddof=1)
                goodRefTaxaCandi = TaxaOverSdThresh[
                    (sdAllTaxa >= np.quantile(sdAllTaxa, SDquantilThresh))
                ]
                rm(sdAllTaxa, posTaxaAll_i, TaxaOverSdThresh)

        if len(goodRefTaxaCandi) == 0:
            print(
                "There are no taxa with SD over the SD quantile threshold:",
                SDquantilThresh,
                ". Try lower the SD quantile threshold",
                "\n",
            )
        rm(w)

    # get predictor data
    predNames = data.columns[data.columns.str.startswith(covsPrefix)].to_numpy()
    nPredics = len(predNames)

    # to add if qualifyreftax
    if qualifyRefTax:
        # find the pairs of binary preds and taxa for which the assocaiton is not identifiable
        if len(binPredInd) > 0:
            allBinPred = predNames[binPredInd]
            nBinPred = len(allBinPred)

            taxaBalanceBin = np.array([])
            bin_nonz_sum = np.array(colSums(qualifyData.loc[:, allBinPred]))

            if np.min((bin_nonz_sum, nSubQualif - bin_nonz_sum)) <= np.floor(
                balanceCut * nSubQualif
            ):
                raise Exception("one of the binary variable is not diverse enough")

            # to add binary loop

            for i in range(nTaxa):
                for j in range(nBinPred):
                    twoColumns_ij = qualifyData.loc[:, [taxaNames[i], allBinPred[j]]]
                    nNonZero = sum(twoColumns_ij.iloc[:, 0] > 0)
                    sumOfBin = sum(
                        twoColumns_ij.loc[(twoColumns_ij.iloc[:, 0] > 0), :].iloc[:, 1]
                    )
                    if np.min((sumOfBin, (nNonZero - sumOfBin))) >= np.floor(
                        balanceCut * nSubQualif
                    ):
                        taxaBalanceBin = np.hstack((taxaBalanceBin, taxaNames[i]))

            taxaBalanceBin = np.unique(taxaBalanceBin)
            # keep balanced taxa
            goodRefTaxaCandi = goodRefTaxaCandi[r_in(goodRefTaxaCandi, taxaBalanceBin)]
        results["goodRefTaxaCandi"] = goodRefTaxaCandi
        rm(goodRefTaxaCandi)

    # return
    results["taxaNames"] = taxaNames
    rm(taxaNames)
    results["predNames"] = predNames
    rm(predNames)
    results["nTaxa"] = nTaxa
    results["nSub"] = nSub
    results["nPredics"] = nPredics
    return results


def dataRecovTrans(data, ref, Mprefix, covsPrefix, xOnly=False, yOnly=False):
    results = {}

    # load A and log-ratio transformed RA
    data_and_init = AIcalcu(data=data, ref=ref, Mprefix=Mprefix, covsPrefix=covsPrefix)
    rm(data)

    taxaNames = data_and_init["taxaNames"]
    A = data_and_init["A"]
    logRatiow = data_and_init["logRatiow"]
    nSub = data_and_init["nSub"]
    nTaxa = data_and_init["nTaxa"]
    xData = data_and_init["xData"]
    nPredics = data_and_init["nPredics"]
    twoList = data_and_init["twoList"]
    lLast = data_and_init["lLast"]
    L = data_and_init["l"]
    lengthTwoList = data_and_init["lengthTwoList"]
    rm(data_and_init)

    nNorm = nTaxa - 1
    xDimension = nPredics + 1  # predictors+intercept

    # create omegaRoot
    omegaRoot = {}
    for j in range(lengthTwoList):
        i = twoList[j]
        if lLast[i] == nTaxa - 1:
            omegaRoot[i] = np.eye(int(L[i] - 1))
        else:
            if L[i] == 2:
                omegaRoot[i] = np.sqrt(0.5)
            else:
                dim = L[i] - 1
                a = (1 + (dim - 2) / 2) / (1 / 2 * (1 + (dim - 1) / 2))
                b = -1 / (1 + (dim - 1) / 2)

                # calculate the square root of omega assuming it is exchangeable
                aStar = dim ** 2 / ((dim - 1) ** 2)
                bStar = b * (dim - 2) / (dim - 1) - a * (dim ** 2 - 2 * dim + 2) / (
                    (dim - 1) ** 2
                )
                cStar = (0.5 * b - 0.5 * a * (dim - 2) / (dim - 1)) ** 2
                cSquare = (-bStar + np.sqrt(bStar ** 2 - 4 * aStar * cStar)) / (
                    2 * aStar
                )

                if cSquare < 0:
                    raise Exception("no solution for square root of omega")

                d = np.sqrt((0.5 * a - cSquare) / (dim - 1))

                if d is None:
                    raise Exception(
                        "no solution for off-diagnal elements for square root of omega"
                    )
                c = (0.5 * b - (dim - 2) * (d ** 2)) / (2 * d)
                omegaRoot[i] = -(
                    (c - d) * np.eye(int(dim)) + d * np.ones((int(dim), int(dim)))
                )

        rm(L, lLast)

    if xOnly:
        # create X_i in the regression equation using Kronecker product
        xDataWithInter = xData.copy()
        xDataWithInter.insert(0, "Intercept", 1)
        xDataWithInter = xDataWithInter.to_numpy()
        rm(xData)

        for j in range(lengthTwoList):
            i = twoList[j]
            xInRegres_i = np.kron(np.eye(nNorm), xDataWithInter[i, :])
            xDataTilda_i = omegaRoot[i] @ A[i] @ xInRegres_i
            rm(xInRegres_i)

            if j == 0:
                xTildalong = xDataTilda_i
            else:
                xTildalong = np.vstack((xTildalong, xDataTilda_i))

        rm(xDataWithInter, xDataTilda_i, omegaRoot, logRatiow)

        results["xTildalong"] = xTildalong
        rm(xTildalong)
        return results

    if yOnly:
        for j in range(lengthTwoList):
            i = twoList[j]
            Utilda_i = omegaRoot[i] @ logRatiow[i]
            if j == 0:
                UtildaLong = Utilda_i
            else:
                UtildaLong = np.hstack((UtildaLong, Utilda_i))

        rm(omegaRoot, logRatiow, Utilda_i)
        results["UtildaLong"] = UtildaLong
        rm(UtildaLong)
        return results

    # if not xOnly and yOnly
    # create X_i in the regression equation using Kronecker product
    xDataWithInter = xData.copy()
    rm(xData)
    xDataWithInter.insert(0, "Inter", 1)
    xDataWithInter = xDataWithInter.to_numpy()

    for j in range(lengthTwoList):
        i = twoList[j]
        xInRegres_i = np.kron(np.eye(nNorm), xDataWithInter[i, :])
        xDataTilda_i = omegaRoot[i] @ A[i] @ xInRegres_i
        rm(xInRegres_i)

        if j == 0:
            xTildalong = xDataTilda_i
        else:
            xTildalong = np.vstack((xTildalong, xDataTilda_i))

    rm(xDataWithInter, xDataTilda_i)

    for j in range(lengthTwoList):
        i = twoList[j]
        Utilda_i = omegaRoot[i] @ logRatiow[i]
        if j == 0:
            UtildaLong = Utilda_i
        else:
            UtildaLong = np.hstack((UtildaLong, Utilda_i))

    rm(omegaRoot, logRatiow, Utilda_i)

    # return objects
    results["UtildaLong"] = UtildaLong
    rm(UtildaLong)
    results["xTildalong"] = xTildalong
    rm(xTildalong)
    results["taxaNames"] = taxaNames
    rm(taxaNames)
    return results


def AIcalcu(data, ref, Mprefix, covsPrefix):
    results = {}
    # get the original sample size
    nSub = nrow(data)
    MVarNamLength = len(Mprefix)

    # get taxa variable names
    microPositions = data.columns.str.startswith(Mprefix)
    nTaxa = len(which(microPositions))
    nNorm = nTaxa - 1
    taxaNames = data.columns[microPositions]
    rm(microPositions)

    # rearrange taxa names
    otherTaxaNames = taxaNames[r_ni(taxaNames, ref)]
    taxaNames = np.hstack([otherTaxaNames, ref])

    # get predictor data
    predNames = data.columns[data.columns.str.startswith(covsPrefix)].to_numpy()
    nPredics = len(predNames)

    # taxa data
    w = data.loc[:, taxaNames]

    # extract x data
    xData = data.loc[:, predNames]
    rm(data, predNames)

    # transform data using log-ratio, creat Ai and Li
    l = np.empty(nSub)
    lLast = np.empty(nSub)
    taxa_non0 = {}
    taxa_0 = {}
    logRatiow = {}
    A = {}

    for i in range(nSub):
        taxa_nonzero = which(w.iloc[i, :] != 0)
        lLast[i] = np.max(taxa_nonzero)
        taxa_zero = which(w.iloc[i, :] == 0)
        taxa_non0[i] = w.iloc[i, taxa_nonzero]
        taxa_0[i] = w.iloc[i, taxa_zero]
        if len(taxa_nonzero) > 0:
            last_nonzero = np.max(taxa_nonzero)
            logwi = np.log(w.iloc[i, taxa_nonzero])
            l[i] = len(logwi)
            if l[i] > 1:
                logRatiow[i] = logwi[:-1:] - logwi[-1]
                zero_m = np.zeros((int(l[i]) - 1, nNorm))
                if last_nonzero == nTaxa - 1:
                    aRow = np.arange(int(l[i]) - 1)
                    aCol = taxa_nonzero[:-1:]
                    zero_m[aRow, aCol] = 1
                else:
                    aRow = np.arange(int(l[i]) - 1)
                    aCol = taxa_nonzero[:-1:]
                    zero_m[aRow, aCol] = 1
                    zero_m[:, int(taxa_nonzero[int(l[i]) - 1])] = -1
                A[i] = zero_m
                rm(zero_m)
            else:
                logRatiow[i] = None
                A[i] = None
        else:
            l[i] = 0
            logRatiow[i] = None
            A[i] = None

    # obtain the list of samples whose have at least 2 non-zero taxa
    twoList = which(l > 1)
    lengthTwoList = len(twoList)

    rm(w)

    results["xData"] = xData
    rm(xData)

    results["logRatiow"] = logRatiow
    rm(logRatiow)
    results["A"] = A
    rm(A)
    results["twoList"] = twoList
    rm(twoList)
    results["taxaNames"] = taxaNames
    rm(taxaNames)
    results["lengthTwoList"] = lengthTwoList
    results["lLast"] = lLast
    results["l"] = l
    results["nTaxa"] = nTaxa
    results["nNorm"] = nNorm
    results["nSub"] = nSub
    results["nPredics"] = nPredics
    return results


def runScrParal(
    data,
    testCovInd,
    testCovInOrder,
    testCovInNewNam,
    nRef,
    paraJobs,
    refTaxa,
    sequentialRun,
    refReadsThresh,
    SDThresh,
    SDquantilThresh,
    balanceCut,
    Mprefix,
    covsPrefix,
    binPredInd,
    adjust_method,
    seed,
    maxDimensionScr=0.8 * 434 * 10 * 10 ** 4,
):

    results = {}

    # load data info
    basicInfo = dataInfo(
        data=data,
        Mprefix=Mprefix,
        covsPrefix=covsPrefix,
        binPredInd=binPredInd,
        refReadsThresh=refReadsThresh,
        SDThresh=SDThresh,
        SDquantilThresh=SDquantilThresh,
        balanceCut=balanceCut,
        qualifyRefTax=True,
    )

    taxaNames = basicInfo["taxaNames"]
    nTaxa = basicInfo["nTaxa"]
    nPredics = basicInfo["nPredics"]
    nSub = basicInfo["nSub"]
    predNames = basicInfo["predNames"]

    results["goodRefTaxaCandi"] = basicInfo["goodRefTaxaCandi"]
    rm(basicInfo)

    nNorm = nTaxa - 1
    nAlphaNoInt = nPredics * nNorm
    nAlphaSelec = nPredics * nTaxa

    # make reference taxa list
    if len(refTaxa) < nRef:
        if seed is not None:
            np.random.seed(seed)
            scipy.random.seed(seed)

        taxon_to_be_sample = results["goodRefTaxaCandi"][
            r_ni(results["goodRefTaxaCandi"], refTaxa)
        ]
        num_to_be_sample = nRef - len(refTaxa)

        if num_to_be_sample >= len(taxon_to_be_sample):
            num_to_be_sample = len(taxon_to_be_sample)
        print(
            "The number of candidate reference taxon is smaller than the number of taxon required in phase 1. The number of taxon was set to be ",
            num_to_be_sample,
        )

        refTaxa_extra = np.random.choice(
            taxon_to_be_sample, num_to_be_sample, replace=False
        )
        refTaxa = np.hstack((refTaxa, refTaxa_extra))

        if len(refTaxa) == 0:
            raise Exception(
                "No candidate reference taxon is available. Please try to lower the reference taxon boundary."
            )

    if len(refTaxa) > nRef:
        if seed is not None:
            np.random.seed(seed)
            scipy.random.seed(seed)
        refTaxa = np.random.choice(refTaxa, nRef, replace=True)

    results["refTaxa"] = np.array(refTaxa)

    # run original data screen
    screen1 = originDataScreen(
        data=data,
        testCovInd=testCovInd,
        nRef=nRef,
        refTaxa=refTaxa,
        paraJobs=paraJobs,
        Mprefix=Mprefix,
        covsPrefix=covsPrefix,
        binPredInd=binPredInd,
        sequentialRun=sequentialRun,
        adjust_method=adjust_method,
        seed=seed,
    )

    results["countOfSelecForAPred"] = screen1["countOfSelecForAPred"]
    results["estOfSelectForAPred"] = screen1["estOfSelectForAPred"]
    results["testCovCountMat"] = screen1["testCovCountMat"]
    results["testEstMat"] = screen1["testEstMat"]

    # rm(screen1)

    nTestCov = len(testCovInd)
    results["nTestCov"] = nTestCov
    results["nTaxa"] = nTaxa
    results["nPredics"] = nPredics

    results["taxaNames"] = taxaNames
    # rm(taxaNames)
    return results


def dataSparsCheck(data, Mprefix):
    results = {}

    # get the original sample size
    nSub = nrow(data)
    MVarNamLength = len(Mprefix)

    # get taxa variable names
    microPositions = data.columns.str.startswith(Mprefix)
    taxaNames = data.columns[microPositions]
    rm(microPositions)

    w = data.loc[:, taxaNames]
    rm(data, taxaNames)
    overallSparsity = np.round(100 * np.mean(w.values == 0), 2)
    print(overallSparsity, "percent of microbiome sequencing reads are zero")

    # check zero taxa and subjects with zero taxa reads
    numTaxaNoReads = sum(colSums(w) == 0)
    if numTaxaNoReads > 0:
        print(
            "There are ",
            numTaxaNoReads,
            " taxa without any sequencing reads and excluded from the analysis",
        )
    rm(numTaxaNoReads)

    numSubNoReads = sum(rowSums(w) == 0)
    if numSubNoReads > 0:
        print(
            "There are ",
            numSubNoReads,
            " subjects without any sequencing reads and excluded from the analysis.",
        )
    rm(numSubNoReads, w)


def Regulariz(
    data,
    testCovInd,
    testCovInOrder,
    testCovInNewNam,
    microbName,
    nRef,
    nRefMaxForEsti,
    refTaxa,
    paraJobs,
    binaryInd,
    binaryInd_test,
    covsPrefix,
    Mprefix,
    fwerRate,
    bootB,
    sequentialRun,
    refReadsThresh,
    SDThresh,
    SDquantilThresh,
    balanceCut,
    adjust_method,
    seed,
):

    results = {}
    regul_start_time = timeit.default_timer()

    nTestCov = len(testCovInd)
    dataSparsCheck(data=data, Mprefix=Mprefix)

    # load abundance data info

    # binCheck = data.loc[:, testCovInNewNam].nunique()
    # binaryInd = which(binCheck == 2)

    data.info = dataInfo(
        data=data, Mprefix=Mprefix, covsPrefix=covsPrefix, binPredInd=binaryInd
    )
    nSub = data.info["nSub"]
    taxaNames = data.info["taxaNames"]
    nPredics = data.info["nPredics"]
    nTaxa = data.info["nTaxa"]
    rm(data.info)

    regul_start_time = timeit.default_timer()
    print("Start Phase 1 analysis")

    selectRegroup = getScrResu(
        data=data,
        testCovInd=testCovInd,
        testCovInOrder=testCovInOrder,
        testCovInNewNam=testCovInNewNam,
        nRef=nRef,
        paraJobs=paraJobs,
        refTaxa=refTaxa,
        sequentialRun=sequentialRun,
        refReadsThresh=refReadsThresh,
        SDThresh=SDThresh,
        SDquantilThresh=SDquantilThresh,
        balanceCut=balanceCut,
        Mprefix=Mprefix,
        covsPrefix=covsPrefix,
        binPredInd=binaryInd,
        adjust_method=adjust_method,
        seed=seed,
    )
    nRef_smaller = np.max((2, math.ceil(nRef / 2)))
    while_loop_ind = False
    loop_num = 0
    print("33 percent of phase 1 analysis has been done")

    while while_loop_ind is False:
        if loop_num >= 2:
            break
        loop_num = loop_num + 1
        refTaxa_smaller = (selectRegroup["goodIndpRefTaxWithCount"].index)[
            :nRef_smaller
        ]

        fin_ref_1 = selectRegroup["finalIndpRefTax"]
        ref_taxa_1 = selectRegroup["refTaxa"]
        selectRegroup = getScrResu(
            data=data,
            testCovInd=testCovInd,
            testCovInOrder=testCovInOrder,
            testCovInNewNam=testCovInNewNam,
            nRef=nRef_smaller,
            paraJobs=paraJobs,
            refTaxa=refTaxa_smaller,
            sequentialRun=sequentialRun,
            refReadsThresh=refReadsThresh,
            SDThresh=SDThresh,
            SDquantilThresh=SDquantilThresh,
            balanceCut=balanceCut,
            Mprefix=Mprefix,
            covsPrefix=covsPrefix,
            binPredInd=binaryInd,
            adjust_method=adjust_method,
            seed=seed,
        )
        fin_ref_2 = selectRegroup["finalIndpRefTax"]
        ref_taxa_2 = selectRegroup["refTaxa"]
        while_loop_ind = np.array_equal(fin_ref_1, fin_ref_2) | np.array_equal(
            ref_taxa_1, ref_taxa_2
        )

        if not while_loop_ind:
            print(
                np.round(100 * (loop_num + 1) / 3, 0),
                " percent of phase 1 analysis has been done",
            )
        if while_loop_ind:
            print("100 percent of phase 1 analysis has been done")

    results["selecCountOverall"] = selectRegroup["selecCountOverall"]
    results["selecCountOverall"].columns = microbName
    results["selecCountMatIndv"] = selectRegroup["selecCountMatIndv"]
    finalIndpRefTax = microbName[r_in(taxaNames, selectRegroup["finalIndpRefTax"])]
    results["finalRefTaxonQualified"] = selectRegroup["refTaxonQualified"]
    results["goodIndpRefTaxLeastCount"] = microbName[
        r_in(taxaNames, selectRegroup["goodIndpRefTaxLeastCount"])
    ]
    results["goodIndpRefTaxWithCount"] = selectRegroup["goodIndpRefTaxWithCount"]
    results["goodIndpRefTaxWithCount"].index = microbName[
        np.hstack(
            [
                which(r_in(taxaNames, i))
                for i in selectRegroup["goodIndpRefTaxWithCount"].index
            ]
        )
    ]

    results["goodIndpRefTaxWithEst"] = selectRegroup["goodIndpRefTaxWithEst"]
    results["goodIndpRefTaxWithEst"].index = microbName[
        np.hstack(
            [
                which(r_in(taxaNames, i))
                for i in selectRegroup["goodIndpRefTaxWithEst"].index
            ]
        )
    ]

    results["goodRefTaxaCandi"] = microbName[
        r_in(taxaNames, selectRegroup["goodRefTaxaCandi"])
    ]
    results["randomRefTaxa"] = microbName[r_in(taxaNames, selectRegroup["refTaxa"])]
    goodIndpRefTax_ascend = results["goodIndpRefTaxWithCount"].sort_values()
    goodIndpRefTaxNam = goodIndpRefTax_ascend.index
    rm(selectRegroup)

    MCPExecuTime = (timeit.default_timer() - regul_start_time) / 60
    results["MCPExecuTime"] = MCPExecuTime
    print("Phase 1 analysis used ", np.round(MCPExecuTime, 2), " minutes")

    results["finalizedBootRefTaxon"] = finalIndpRefTax

    startT = timeit.default_timer()
    print("Start Phase 2 parameter estimation")

    qualifyData = data

    if len(binaryInd_test) > 0:
        qualifyData = data.loc[rowSums(data.loc[:, taxaNames] > 0) >= 2, :]
        allBinPred = [covsPrefix + str(i + 1) for i in binaryInd_test]
        nBinPred = len(allBinPred)

        # find the pairs of binary preds and taxa for which the assocaiton is not identifiable
        AllTaxaNamesNoRefTax = taxaNames[
            ~r_in(microbName, results["finalizedBootRefTaxon"])
        ]
        unbalanceTaxa = np.empty(0)
        unbalancePred = np.empty(0)

        for i in AllTaxaNamesNoRefTax:
            for j in allBinPred:
                twoColumns_ij = qualifyData.loc[:, [i, j]]
                nNonZero = sum(twoColumns_ij.iloc[:, 0] > 0)
                sumOfBin = sum(
                    twoColumns_ij.loc[(twoColumns_ij.iloc[:, 0] > 0), :].iloc[:, 1]
                )
                if r_in([sumOfBin], [0, 1, (nNonZero - 1), nNonZero]):
                    unbalanceTaxa = np.hstack((unbalanceTaxa, i))
                    unbalancePred = np.hstack((unbalancePred, j))

        if len(unbalanceTaxa) > 0:
            unbalanceTaxa_ori_name = microbName.take(
                [np.where(r_in(taxaNames, xx)) for xx in unbalanceTaxa]
            ).flatten()
            unbalancePred_ori_name = testCovInOrder.take(
                [np.where(r_in(testCovInNewNam, xx)) for xx in unbalancePred]
            ).flatten()
        else:
            unbalanceTaxa_ori_name = np.empty(0)
            unbalancePred_ori_name = np.empty(0)
    else:
        unbalanceTaxa_ori_name = np.empty(0)
        unbalancePred_ori_name = np.empty(0)

    # check zero taxa and subjects with zero taxa reads

    # numpy unique will sort it !! avoid it by pandas
    allRefTaxNam = pd.unique(
        np.concatenate((results["finalizedBootRefTaxon"], goodIndpRefTaxNam))
    )
    nGoodIndpRef = len(allRefTaxNam)
    results["allRefTaxNam"] = allRefTaxNam

    results["nRefUsedForEsti"] = np.min((nGoodIndpRef, nRefMaxForEsti))

    results["estiList"] = {}

    # allRefTaxNam = np.array(["rawCount12", "rawCount31"])

    for iii in range(results["nRefUsedForEsti"]):
        print("Start estimation for the ", iii + 1, "th final reference taxon")
        time11 = timeit.default_timer()
        originTaxNam = allRefTaxNam[iii]
        newRefTaxNam = taxaNames[r_in(microbName, originTaxNam)]
        results["estiList"][originTaxNam] = bootResuHDCI(
            data=data,
            refTaxa=newRefTaxNam,
            originRefTaxNam=originTaxNam,
            bootB=bootB,
            binPredInd=binaryInd,
            covsPrefix=covsPrefix,
            Mprefix=Mprefix,
            unbalanceTaxa_ori_name=unbalanceTaxa_ori_name,
            unbalancePred_ori_name=unbalancePred_ori_name,
            testCovInOrder=testCovInOrder,
            adjust_method=adjust_method,
            microbName=microbName,
            fwerRate=fwerRate,
            paraJobs=paraJobs,
            sequentialRun=sequentialRun,
            seed=seed,
        )
        time12 = timeit.default_timer()
        print(
            "Estimation done for the ",
            iii + 1,
            "th final reference taxon and it took ",
            round((time12 - time11) / 60, 3),
            " minutes",
        )

    endT = timeit.default_timer()

    print(
        "Phase 2 parameter estimation done and took ",
        round((endT - startT) / 60, 3),
        " minutes.",
    )

    ### calculate mean ###
    fin_ref_taxon_name = np.array(list(results["estiList"].keys()))

    all_cov_sig_list = {}
    all_cov_list = {}

    for i in range(len(fin_ref_taxon_name)):
        i_name = fin_ref_taxon_name[i]
        all_cov_list[i_name] = results["estiList"][i_name]["all_cov_list"]
        all_cov_sig_list[i_name] = results["estiList"][i_name]["sig_list_each"]

    results["all_cov_list"] = all_cov_list
    results["all_cov_sig_list"] = all_cov_sig_list

    ref_taxon_name = np.array(list(all_cov_list.keys()))

    all_cov_list_0 = all_cov_list[ref_taxon_name[0]]
    all_cov_list_1 = all_cov_list[ref_taxon_name[1]]

    exclu_0 = r_ni(colnames(all_cov_list_0["est_save_mat"]), ref_taxon_name[1])
    exclu_1 = r_ni(colnames(all_cov_list_1["est_save_mat"]), ref_taxon_name[0])

    est_save_mat_mean = (
        all_cov_list_0["est_save_mat"].loc[:, exclu_0]
        + all_cov_list_1["est_save_mat"].loc[:, exclu_1]
    ) / 2
    se_mat_mean = (
        all_cov_list_0["se_mat"].loc[:, exclu_0]
        + all_cov_list_1["se_mat"].loc[:, exclu_1]
    ) / 2
    CI_low_mat_mean = (
        all_cov_list_0["CI_low_mat"].loc[:, exclu_0]
        + all_cov_list_1["CI_low_mat"].loc[:, exclu_1]
    ) / 2
    CI_up_mat_mean = (
        all_cov_list_0["CI_up_mat"].loc[:, exclu_0]
        + all_cov_list_1["CI_up_mat"].loc[:, exclu_1]
    ) / 2

    p_value_unadj_mean = (est_save_mat_mean / se_mat_mean).apply(
        lambda x: (1 - scipy.stats.norm.cdf(np.abs(x))) * 2,
    )

    p_value_adj_mean = p_value_unadj_mean.apply(
        lambda x: multipleTest(x, method=adjust_method), axis=1, result_type="expand",
    )

    p_value_adj_mean.columns = p_value_unadj_mean.columns

    colname_use = colnames(est_save_mat_mean)

    sig_ind = np.where((p_value_adj_mean < fwerRate).to_numpy())
    sig_row = sig_ind[0]
    sig_col = sig_ind[1]

    est_sig = [
        est_save_mat_mean.iloc[sig_row[my_i], sig_col[my_i]]
        for my_i in range(len(sig_row))
    ]
    CI_low_sig = [
        CI_low_mat_mean.iloc[sig_row[my_i], sig_col[my_i]]
        for my_i in range(len(sig_row))
    ]
    CI_up_sig = [
        CI_up_mat_mean.iloc[sig_row[my_i], sig_col[my_i]]
        for my_i in range(len(sig_row))
    ]
    p_adj_sig = [
        p_value_adj_mean.iloc[sig_row[my_i], sig_col[my_i]]
        for my_i in range(len(sig_row))
    ]
    se_sig = [
        se_mat_mean.iloc[sig_row[my_i], sig_col[my_i]] for my_i in range(len(sig_row))
    ]

    est_sig = np.array(est_sig)
    CI_low_sig = np.array(CI_low_sig)
    CI_up_sig = np.array(CI_up_sig)
    p_adj_sig = np.array(p_adj_sig)
    se_sig = np.array(se_sig)

    cov_sig_index = np.sort(np.unique(sig_row))

    sig_list_each_mean = {}

    if len(cov_sig_index) > 0:
        for iii in range(len(cov_sig_index)):
            sig_loc = which(sig_row == cov_sig_index[iii]).astype(int)
            est_spe_cov = est_sig[sig_loc]
            CI_low_spe_cov = CI_low_sig[sig_loc]
            CI_up_spe_cov = CI_up_sig[sig_loc]
            p_adj_spe_cov = p_adj_sig[sig_loc]
            se_spe_cov = se_sig[sig_loc]

            cov_sig_mat = np.zeros((len(sig_loc), 5))
            cov_sig_mat = pd.DataFrame(
                cov_sig_mat,
                columns=["estimate", "SE est", "CI low", "CI up", "adj p-value"],
            )
            cov_sig_mat.iloc[:, 0] = est_spe_cov
            cov_sig_mat.iloc[:, 1] = se_spe_cov
            cov_sig_mat.iloc[:, 2] = CI_low_spe_cov
            cov_sig_mat.iloc[:, 3] = CI_up_spe_cov
            cov_sig_mat.iloc[:, 4] = p_adj_spe_cov

            cov_sig_mat.index = colname_use[sig_col[sig_loc]]
            sig_list_each_mean[testCovInOrder[cov_sig_index[iii]]] = cov_sig_mat

    results["sig_results"] = sig_list_each_mean
    full_results = {}

    for j in range(len(testCovInOrder)):
        j_name = testCovInOrder[j]
        est_res_save_all = pd.concat(
            (
                est_save_mat_mean.loc[j_name,],
                se_mat_mean.loc[j_name,],
                CI_low_mat_mean.loc[j_name,],
                CI_up_mat_mean.loc[j_name,],
                p_value_adj_mean.loc[j_name,],
            ),
            axis=1,
        )
        est_res_save_all.columns = [
            "estimate",
            "SE est",
            "CI low",
            "CI up",
            "adj p-value",
        ]
        full_results[j_name] = est_res_save_all

    results["full_results"] = full_results

    results["nTaxa"] = nTaxa
    results["nPredics"] = nPredics

    # return results

    results["nRef"] = nRef
    return results


def getScrResu(
    data,
    testCovInd,
    testCovInOrder,
    testCovInNewNam,
    nRef,
    paraJobs,
    refTaxa,
    sequentialRun,
    refReadsThresh,
    SDThresh,
    SDquantilThresh,
    balanceCut,
    Mprefix,
    covsPrefix,
    binPredInd,
    adjust_method,
    seed,
    goodIndeCutPerc=0.33,
):
    results = {}
    # run permutation
    scrParal = runScrParal(
        data=data,
        testCovInd=testCovInd,
        testCovInOrder=testCovInOrder,
        testCovInNewNam=testCovInNewNam,
        nRef=nRef,
        paraJobs=paraJobs,
        refTaxa=refTaxa,
        sequentialRun=sequentialRun,
        refReadsThresh=refReadsThresh,
        SDThresh=SDThresh,
        SDquantilThresh=SDquantilThresh,
        balanceCut=balanceCut,
        Mprefix=Mprefix,
        covsPrefix=covsPrefix,
        binPredInd=binPredInd,
        adjust_method=adjust_method,
        seed=seed,
    )

    selecCountOverall = scrParal["countOfSelecForAPred"]
    selecEstOverall = scrParal["estOfSelectForAPred"]

    selecCountMatIndv = scrParal["testCovCountMat"]
    selecEstMatIndv = scrParal["testEstMat"]

    taxaNames = scrParal["taxaNames"]
    goodRefTaxaCandi = scrParal["goodRefTaxaCandi"]

    nTaxa = scrParal["nTaxa"]
    nPredics = scrParal["nPredics"]
    nTestCov = scrParal["nTestCov"]
    results["refTaxa"] = scrParal["refTaxa"]
    # rm(scrParal)

    if nTestCov == 1:
        results["selecCountMatIndv"] = selecCountOverall
        results["selecEstMatIndv"] = selecEstOverall
    if nTestCov > 1:
        results["selecCountMatIndv"] = selecCountMatIndv
        results["selecEstMatIndv"] = selecEstMatIndv
        rm(selecCountMatIndv)

    goodIndpRefTaxWithCount = selecCountOverall.iloc[
        0, r_in(colnames(selecCountOverall), goodRefTaxaCandi)
    ]
    goodIndpRefTaxWithEst = selecEstOverall.iloc[
        0, r_in(colnames(selecEstOverall), goodRefTaxaCandi)
    ]

    if len(goodIndpRefTaxWithCount) == 0:
        results["goodIndpRefTaxLeastCount"] = np.array([])
    else:
        results["goodIndpRefTaxLeastCount"] = goodIndpRefTaxWithCount.index[
            np.lexsort((np.abs(goodIndpRefTaxWithEst), goodIndpRefTaxWithCount))
        ][0:2]
        goodIndpRefTaxWithEst = np.abs(
            goodIndpRefTaxWithEst[
                np.lexsort((np.abs(goodIndpRefTaxWithEst), goodIndpRefTaxWithCount))
            ]
        )
        goodIndpRefTaxWithCount = goodIndpRefTaxWithCount[
            np.lexsort((np.abs(goodIndpRefTaxWithEst), goodIndpRefTaxWithCount))
        ]

    results["selecCountOverall"] = selecCountOverall
    results["goodIndpRefTaxWithCount"] = goodIndpRefTaxWithCount
    results["goodIndpRefTaxWithEst"] = goodIndpRefTaxWithEst
    results["goodRefTaxaCandi"] = goodRefTaxaCandi
    rm(goodRefTaxaCandi)
    results["refTaxonQualified"] = 2
    results["finalIndpRefTax"] = results["goodIndpRefTaxLeastCount"]

    return results


def originDataScreen(
    data,
    testCovInd,
    nRef,
    paraJobs,
    refTaxa,
    sequentialRun,
    Mprefix,
    covsPrefix,
    binPredInd,
    adjust_method,
    seed,
    maxDimensionScr=434 * 5 * 10 ** 5,
):

    results = {}

    # load data info
    basicInfo = dataInfo(
        data=data, Mprefix=Mprefix, covsPrefix=covsPrefix, binPredInd=binPredInd
    )

    taxaNames = basicInfo["taxaNames"]
    nTaxa = basicInfo["nTaxa"]
    nPredics = basicInfo["nPredics"]
    rm(basicInfo)

    nNorm = nTaxa - 1
    nAlphaNoInt = nPredics * nNorm
    nAlphaSelec = nPredics * nTaxa

    countOfSelec = np.zeros(nAlphaSelec)

    # overwrite nRef if the reference taxon is specified
    nRef = len(refTaxa)

    forEachUnitRun_partial = partial(
        forEachUnitRun,
        taxaNames,
        refTaxa,
        Mprefix,
        covsPrefix,
        maxDimensionScr,
        nPredics,
        data,
        nAlphaSelec,
        nAlphaNoInt,
        nTaxa,
        seed,
    )

    startT1 = timeit.default_timer()
    if len(paraJobs) == 0:
        availCores = mp.cpu_count()
        if isinstance(availCores, int):
            paraJobs = max(1, availCores - 2)

    if not sequentialRun:
        print(
            paraJobs,
            " parallel jobs are registered for analyzing ",
            nRef,
            " reference taxa in Phase 1",
        )

        with tqdm_joblib(tqdm(desc="Phase1-Par", total=nRef)) as progress_bar:
            scr1Resu = Parallel(n_jobs=int(paraJobs))(
                delayed(forEachUnitRun_partial)(i) for i in range(nRef)
            )

    if sequentialRun:
        print(
            " Sequential running analysis for ", nRef, " reference taxa in Phase 1",
        )

        scr1Resu = [
            forEachUnitRun_partial(i) for i in tqdm(range(nRef), desc="Phase1-Seq")
        ]

    endT = timeit.default_timer()

    scr1ResuSelec = np.hstack([i["selection"][:, np.newaxis] for i in scr1Resu])
    scr1ResuEst = np.hstack([i["coef"][:, np.newaxis] for i in scr1Resu])

    # create count of selection for individual testCov
    countOfSelecForAllPred = scr1ResuSelec.sum(axis=1).reshape((-1, nPredics))
    countOfSelecForAllPred = np.transpose(countOfSelecForAllPred)
    EstOfAllPred = scr1ResuEst.sum(axis=1).reshape((-1, nPredics))
    EstOfAllPred = np.transpose(EstOfAllPred)

    testCovCountMat = countOfSelecForAllPred[testCovInd, :]
    testEstMat = EstOfAllPred[testCovInd, :]
    # rm(scr1ResuSelec, testCovInd, countOfSelecForAllPred, EstOfAllPred)

    # create overall count of selection for all testCov as a whole
    countOfSelecForAPred = testCovCountMat.sum(axis=0).reshape((1, -1))
    estOfSelectForAPred = testEstMat.sum(axis=0).reshape((1, -1))

    countOfSelecForAPred = pd.DataFrame(countOfSelecForAPred)
    estOfSelectForAPred = pd.DataFrame(estOfSelectForAPred)

    countOfSelecForAPred.columns = taxaNames
    estOfSelectForAPred.columns = taxaNames
    # return results
    results["testCovCountMat"] = testCovCountMat
    results["testEstMat"] = testEstMat
    # rm(testCovCountMat, testEstMat)
    results["countOfSelecForAPred"] = countOfSelecForAPred
    results["estOfSelectForAPred"] = estOfSelectForAPred
    # rm(countOfSelecForAPred, estOfSelectForAPred)
    return results


def forEachUnitRun(
    taxaNames,
    refTaxa,
    Mprefix,
    covsPrefix,
    maxDimensionScr,
    nPredics,
    data,
    nAlphaSelec,
    nAlphaNoInt,
    nTaxa,
    seed,
    i,
):

    np.random.seed(seed + i)
    scipy.random.seed(seed + i)

    ii = which(taxaNames == refTaxa[i])
    dataForEst = dataRecovTrans(
        data=data, ref=refTaxa[i], Mprefix=Mprefix, covsPrefix=covsPrefix
    )

    xTildLongTild_i = dataForEst["xTildalong"]
    yTildLongTild_i = dataForEst["UtildaLong"]
    # rm(dataForEst)

    maxSubSamplSiz = np.min(
        (50000.0, np.floor(maxDimensionScr / xTildLongTild_i.shape[1]))
    ).astype(int)

    nToSamplFrom = xTildLongTild_i.shape[0]

    subSamplK = np.ceil(nToSamplFrom / maxSubSamplSiz).astype(int)

    if subSamplK == 1:
        maxSubSamplSiz = nToSamplFrom

    nRuns = np.ceil(subSamplK / 3).astype(int)

    # ChangePoint
    # nRuns = 3
    # maxSubSamplSiz = int(nToSamplFrom / 2)

    for k in range(nRuns):
        np.random.seed(int(seed + k))
        rowToKeep = np.random.choice(nToSamplFrom, maxSubSamplSiz, replace=False)
        x = xTildLongTild_i[rowToKeep, :]
        y = yTildLongTild_i[rowToKeep]

        if x.shape[0] > (3 * x.shape[1]): # ChangePoint
            Penal_i = runlinear(x=x, y=y, nPredics=nPredics)
            BetaNoInt_k = (Penal_i["betaNoInt"] != 0).astype(int)
            EstNoInt_k = np.abs(Penal_i["coef_est_noint"])
        else:
            Penal_i = runGlmnet(x=x, y=y, nPredics=nPredics)
            BetaNoInt_k = (Penal_i["betaNoInt"] != 0).astype(int)
            EstNoInt_k = np.abs(Penal_i["betaNoInt"])

        if k == 0:
            BetaNoInt_i = BetaNoInt_k
            EstNoInt_i = EstNoInt_k
        if k > 0:
            BetaNoInt_i = BetaNoInt_i + BetaNoInt_k
            EstNoInt_i = EstNoInt_i + EstNoInt_k

    BetaNoInt_i = BetaNoInt_i / nRuns
    EstNoInt_i = EstNoInt_i / nRuns
    selection_i = np.zeros(nAlphaSelec)
    coef_i = np.zeros(nAlphaSelec)

    if ii == 0:
        np_assign_but(selection_i, np.linspace(0, nPredics - 1, nPredics), BetaNoInt_i)
        np_assign_but(coef_i, np.linspace(0, nPredics - 1, nPredics), EstNoInt_i)
    if ii == (nTaxa - 1):
        np_assign_but(
            selection_i,
            np.linspace(nAlphaSelec - nPredics, nAlphaSelec - 1, nPredics),
            BetaNoInt_i,
        )
        np_assign_but(
            coef_i,
            np.linspace(nAlphaSelec - nPredics, nAlphaSelec - 1, nPredics),
            EstNoInt_i,
        )
    if (ii > 0) & (ii < (nTaxa - 1)):
        selection_i[0 : int((nPredics * (ii)))] = BetaNoInt_i[
            0 : int((nPredics * (ii)))
        ]
        selection_i[int(nPredics * (ii + 1)) : (nAlphaSelec)] = BetaNoInt_i[
            int(nPredics * (ii)) : (nAlphaNoInt + 1)
        ]
        coef_i[0 : int((nPredics * (ii)))] = EstNoInt_i[0 : int((nPredics * (ii)))]
        coef_i[int(nPredics * (ii + 1)) : (nAlphaSelec)] = EstNoInt_i[
            int(nPredics * (ii)) : (nAlphaNoInt + 1)
        ]
    # rm(BetaNoInt_i)
    # create return vector
    recturnlist = {}
    recturnlist["selection"] = selection_i
    recturnlist["coef"] = coef_i
    return recturnlist


def runlinear(x, y, nPredics, fwerRate=0.25, adjust_method="fdr_bh"):
    results = {}

    print("runLinear Phase I")

    mask = np.ones(x.shape[1], dtype=bool)
    # denote linear dependent columns
    ld_col = detectLDcol(x)
    mask[ld_col] = False
    # denote constant columns
    cons_col = detectCcol(x)
    mask[cons_col] = False

    lm_res = OLS(y, x[:, mask]).fit()

    p_value_est = np.empty(x.shape[1])
    p_value_est[mask] = lm_res.pvalues
    p_value_est[~mask] = np.nan

    disc_index = np.arange(0, len(p_value_est), (nPredics + 1))
    p_value_est_noint = np.delete(p_value_est, disc_index, axis=0)

    # this method automatically convert over 1 values to 1
    p_value_est_noint_adj = multipleTest(p_value_est_noint, method=adjust_method)
    p_value_est_noint_adj[~np.isfinite(p_value_est_noint_adj)] = 1

    coef_est = np.empty(x.shape[1])
    coef_est[mask] = np.abs(lm_res.params)
    coef_est[~mask] = np.nan

    disc_index = np.arange(0, len(coef_est), (nPredics + 1))
    coef_est_noint = np.delete(coef_est, disc_index, axis=0)
    coef_est_noint[~np.isfinite(coef_est_noint)] = np.nanmax(coef_est_noint)

    # return
    results["betaNoInt"] = p_value_est_noint_adj < fwerRate
    results["betaInt"] = p_value_est
    results["coef_est_noint"] = coef_est_noint

    return results


def detectLDcol(mat):
    """
    Detect Linear Dependent Columns in a matrix
    https://stackoverflow.com/questions/53667174/elimination-the-linear-dependent-columns-of-a-non-square-matrix-in-python
    """

    # add constant columns
    # test which is faster

    q, r, p = scipy.linalg.qr(mat, pivoting=True)
    rank = np.linalg.matrix_rank(mat)
    return np.sort(p[rank:])


def detectLDcolNP(mat):
    """
    Detect Linear Dependent Columns in a matrix
    https://stackoverflow.com/questions/53667174/elimination-the-linear-dependent-columns-of-a-non-square-matrix-in-python
    """

    # add constant columns
    # test which is faster

    q, r = np.linalg.qr(mat)
    return which(np.abs(np.diag(r)) <= 1e-10)


def detectCcol(mat, tol=1e-19):
    return which(np.std(mat, axis=0, ddof=1) <= tol)


def multipleTest(p, method):

    # R's p.adjust(*, method)
    p=p.copy()
    p0 = p
    nna = np.isfinite(p)
    if not all(nna):
        p = p[nna]
    lp = len(p)

    if method == "fdr_bh":
        i = np.array(list(range(lp, 0, -1)))
        o = np.argsort(-p) + 1
        ro = np.argsort(o) + 1
        p0[nna] = np.minimum(1, np.minimum.accumulate(len(p) / i * p[o - 1]))[ro - 1]

    if method == "fdr_by":
        i = np.array(list(range(lp, 0, -1)))
        o = np.argsort(-p) + 1
        ro = np.argsort(o) + 1
        q = np.sum(1 / np.arange(1, len(p) + 1))
        p0[nna] = np.minimum(1, np.minimum.accumulate(q * len(p) / i * p[o - 1]))[
            ro - 1
        ]

    return p0


def runGlmnet(
    x,
    y,
    nPredics,
    standardize=False,
    family="gaussian",
    nfolds=10,
    lambda_min_ratio=0.05,
    nLam=100,
    intercept=True,
    zeroSDCut=10 ** (-20),
):
    print("runGlmnet Phase I")
    results = {}
    nBeta = x.shape[1]

    # remove near constant x columns
    sdX = np.std(x, axis=0, ddof=1)
    xWithNearZeroSd = which(sdX <= zeroSDCut)
    if len(xWithNearZeroSd) > 0:
        x = np.delete(x, xWithNearZeroSd, axis=1)

    np.random.seed(1)
    foldid = np.random.choice(int(10), int(len(y)), replace=True)

    cvResul = cvglmnet(
        x=x.copy(),
        y=y.copy(),
        alpha=1,
        nlambda=nLam,
        standardize=standardize,
        intr=intercept,
        family=family,
        foldid=foldid,
    )

    finalLassoRunBeta = cvglmnetCoef(cvResul, s="lambda_min")[1:].flatten()

    # convert back to the full beta if there near constant x columns
    if len(xWithNearZeroSd) > 0:
        betaTrans = groupBetaToFullBeta(
            nTaxa=nBeta,
            nPredics=1,
            unSelectList=np.sort(xWithNearZeroSd),
            newBetaNoInt=finalLassoRunBeta,
        )
        beta = betaTrans["finalBeta"]
    else:
        beta = finalLassoRunBeta

    disc_index = np.arange(0, len(beta), (nPredics + 1))
    results["betaNoInt"] = np.delete(beta, disc_index, axis=0)

    return results


def groupBetaToFullBeta(nTaxa, nPredics, unSelectList, newBetaNoInt):
    print("Called groupBetaToFullBeta")
    results = {}
    unSelectList = np.unique(np.sort(unSelectList))
    nUnSelec = len(unSelectList)
    nAlphaSelec = nTaxa * nPredics
    nNewBetaNoInt = len(newBetaNoInt)

    if nNewBetaNoInt != ((nTaxa - nUnSelec) * nPredics):
        raise Exception(
            "Error: Beta dimension from grouped analyis does not match the expected number"
        )

    if nTaxa < np.max(unSelectList) | 1 > np.min(unSelectList):
        raise Exception("Error: unSelectList out of range")

    finalBeta = newBetaNoInt

    for i in unSelectList:
        finalBetaTemp = np.empty((len(finalBeta) + nPredics))
        lengthTemp = len(finalBetaTemp)

        if i == 1:
            finalBetaTemp[0:nPredics] = 0
            finalBetaTemp[nPredics : (lengthTemp + 1)] = finalBeta
            finalBeta = finalBetaTemp

        if i > 1:
            if (i * nPredics) <= len(finalBeta):
                finalBetaTemp[0 : ((i - 1) * nPredics)] = finalBeta[
                    0 : ((i - 1) * nPredics)
                ]
                finalBetaTemp[((i - 1) * nPredics) : (i * nPredics)] = 0
                finalBetaTemp[(i * nPredics) : lengthTemp] = finalBeta[
                    ((i - 1) * nPredics) : (len(finalBeta))
                ]
            else:
                finalBetaTemp[0 : ((i - 1) * nPredics)] = finalBeta
                finalBetaTemp[((i - 1) * nPredics) : lengthTemp] = 0

            finalBeta = finalBetaTemp

    results["finalBeta"] = finalBeta
    return results


def bootResuHDCI(
    data,
    refTaxa,
    originRefTaxNam,
    bootB,
    binPredInd,
    covsPrefix,
    Mprefix,
    unbalanceTaxa_ori_name,
    unbalancePred_ori_name,
    testCovInOrder,
    adjust_method,
    microbName,
    fwerRate,
    paraJobs,
    sequentialRun,
    seed,
    maxDimension=434 * 5 * 10 ** 5,
    bootLassoAlpha=0.05,
):

    results = {}

    # load data info
    basicInfo = dataInfo(
        data=data, Mprefix=Mprefix, covsPrefix=covsPrefix, binPredInd=binPredInd
    )

    taxaNames = basicInfo["taxaNames"]
    ii = which(r_in(basicInfo["taxaNames"], refTaxa))
    nTaxa = basicInfo["nTaxa"]
    nPredics = basicInfo["nPredics"]
    rm(basicInfo)

    nNorm = nTaxa - 1
    nAlphaNoInt = nPredics * nNorm
    nAlphaSelec = nPredics * nTaxa

    countOfSelec = np.zeros(nAlphaSelec)

    resultsByRefTaxon = {}

    # inital Lasso OLS estimate
    dataForEst = dataRecovTrans(
        data=data, ref=refTaxa, Mprefix=Mprefix, covsPrefix=covsPrefix
    )

    x = dataForEst["xTildalong"]
    y = dataForEst["UtildaLong"]

    # rm(dataForEst)

    xCol = x.shape[1]

    maxSubSamplSiz = np.min((50000, math.floor(maxDimension / xCol)))
    nToSamplFrom = len(y)
    subSamplK = math.ceil(nToSamplFrom / maxSubSamplSiz)
    if subSamplK == 1:
        maxSubSamplSiz = nToSamplFrom

    nRuns = math.ceil(subSamplK / 3)

    # ChangePoint
    # nRuns = 3
    # maxSubSamplSiz = int(nToSamplFrom / 2)

    if x.shape[0] > x.shape[1]:  #  True:  #  ## ChangePoint
        for k in range(nRuns):
            np.random.seed(int(seed + k))
            rowToKeep = np.random.choice(nToSamplFrom, maxSubSamplSiz, replace=False)
            xSub = x[rowToKeep, :]
            ySub = y[rowToKeep]

            print("runLinear Phase 2")

            # remove all constant column see email thread
            mask = np.ones(xSub.shape[1], dtype=bool)
            # denote linear dependent columns
            ld_col = detectLDcol(xSub)
            mask[ld_col] = False
            # denote constant columns
            cons_col = detectCcol(xSub)
            mask[cons_col] = False

            lm_res = OLS(ySub, xSub[:, mask]).fit()

            params, bse, tvalues, pvalues = (
                np.empty(x.shape[1]),
                np.empty(x.shape[1]),
                np.empty(x.shape[1]),
                np.empty(x.shape[1]),
            )
            params[mask], bse[mask], tvalues[mask], pvalues[mask] = (
                lm_res.params,
                lm_res.bse,
                lm_res.tvalues,
                lm_res.pvalues,
            )
            params[~mask], bse[~mask], tvalues[~mask], pvalues[~mask] = (
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            )

            # lm_res.summary()
            # lm_res.params
            # lm_res.bse
            # lm_res.tvalues
            # lm_res.pvalues

            bootResu = np.transpose(np.vstack((params, bse, tvalues, pvalues)))

            if k == 0:
                bootResu_k = bootResu
            else:
                bootResu_k = bootResu_k + bootResu

        fin_ref_taxon_name = originRefTaxNam
        all_cov_list = {}
        nTestcov = len(testCovInOrder)

        boot_est = bootResu_k[:, 0] / nRuns
        se_est_all = bootResu_k[:, 1] / nRuns
        # Unusable variable, remember to remove NAs if want to use
        # boot_CI = lm_res.conf_int()

        ref_taxon_name = originRefTaxNam

        p_value_save_mat = np.zeros((nTestcov, nTaxa - 1))
        est_save_mat = np.zeros((nTestcov, nTaxa - 1))
        CI_up_mat = np.zeros((nTestcov, nTaxa - 1))
        CI_low_mat = np.zeros((nTestcov, nTaxa - 1))
        se_mat = np.zeros((nTestcov, nTaxa - 1))

        for ii in range(nTestcov):
            se_est = se_est_all[(ii + 1) : len(params) : (nPredics + 1)]
            boot_est_par = boot_est[(ii + 1) : len(params) : (nPredics + 1)]

            p_value_unadj = (
                1 - scipy.stats.norm.cdf(np.abs(boot_est_par / se_est))
            ) * 2
            boot_est_CI_low = boot_est_par - 1.96 * se_est
            boot_est_CI_up = boot_est_par + 1.96 * se_est

            p_value_adj = multipleTest(p_value_unadj, adjust_method)

            p_value_save_mat[ii, :] = p_value_adj
            est_save_mat[ii,] = boot_est_par
            CI_low_mat[ii,] = boot_est_CI_low
            CI_up_mat[ii,] = boot_est_CI_up
            se_mat[ii,] = se_est

    else:
        for k in range(nRuns):

            np.random.seed(int(seed + k))
            rowToKeep = np.random.choice(nToSamplFrom, maxSubSamplSiz, replace=False)
            xSub = x[rowToKeep, :]
            ySub = y[rowToKeep]

            print("runGlmnet Phase 2")

            bootResu = runBootLassoHDCI(
                x=xSub,
                y=ySub,
                paraJobs=paraJobs,
                sequentialRun=sequentialRun,
                bootLassoAlpha=bootLassoAlpha,
                seed=seed,
                bootB=bootB,
            )

            if k == 0:
                boot_est_k = bootResu["Beta_LPR"]
                boot_CI_k = bootResu["interval_LPR"]
            else:
                boot_est_k = boot_est_k + bootResu["Beta_LPR"]
                boot_CI_k = boot_CI_k + bootResu["interval_LPR"]

        results["reg_res"] = bootResu
        fin_ref_taxon_name = originRefTaxNam
        all_cov_list = {}
        nTestcov = len(testCovInOrder)

        boot_est = boot_est_k / nRuns
        boot_CI = boot_CI_k / nRuns
        ref_taxon_name = originRefTaxNam
        p_value_save_mat = np.zeros((nTestcov, nTaxa - 1))
        est_save_mat = np.zeros((nTestcov, nTaxa - 1))
        CI_up_mat = np.zeros((nTestcov, nTaxa - 1))
        CI_low_mat = np.zeros((nTestcov, nTaxa - 1))
        se_mat = np.zeros((nTestcov, nTaxa - 1))
        for ii in range(nTestcov):
            se_est = np.apply_along_axis(
                partial(calculate_se, bootLassoAlpha),
                axis=0,
                arr=boot_CI[:, (ii + 1) : boot_CI.shape[1] : (nPredics + 1)],
            )

            p_value_unadj = np.zeros(len(se_est))
            # p_value_unadj=(1-scipy.stats.norm.cdf(np.abs(boot_est_par/se_est)))*2

            boot_est_par = boot_est[(ii + 1) : boot_CI.shape[1] : (nPredics + 1)]
            boot_est_CI_low = boot_CI[0, (ii + 1) : boot_CI.shape[1] : (nPredics + 1)]
            boot_est_CI_up = boot_CI[1, (ii + 1) : boot_CI.shape[1] : (nPredics + 1)]

            for j in range(len(boot_est_par)):
                if se_est[j] == 0:
                    p_value_unadj[j] = 1
                else:
                    p_value_unadj[j] = (
                        1 - scipy.stats.norm.cdf(np.abs(boot_est_par[j] / se_est[j]))
                    ) * 2
            p_value_adj = multipleTest(p_value_unadj, method=adjust_method)
            p_value_save_mat[ii, :] = p_value_adj
            est_save_mat[ii,] = boot_est_par
            CI_low_mat[ii,] = boot_est_CI_low
            CI_up_mat[ii,] = boot_est_CI_up
            se_mat[ii,] = se_est

    colname_use = microbName[microbName != ref_taxon_name]

    p_value_save_mat = pd.DataFrame(
        p_value_save_mat, index=testCovInOrder, columns=colname_use
    )
    est_save_mat = pd.DataFrame(est_save_mat, index=testCovInOrder, columns=colname_use)
    CI_low_mat = pd.DataFrame(CI_low_mat, index=testCovInOrder, columns=colname_use)
    CI_up_mat = pd.DataFrame(CI_up_mat, index=testCovInOrder, columns=colname_use)
    se_mat = pd.DataFrame(se_mat, index=testCovInOrder, columns=colname_use)

    if len(unbalanceTaxa_ori_name) > 0:
        est_save_mat[cbind(unbalancePred_ori_name, unbalanceTaxa_ori_name)] = -1000
        CI_low_mat[cbind(unbalancePred_ori_name, unbalanceTaxa_ori_name)] = -1000
        CI_up_mat[cbind(unbalancePred_ori_name, unbalanceTaxa_ori_name)] = -1000
        se_mat[cbind(unbalancePred_ori_name, unbalanceTaxa_ori_name)] = -1000
        p_value_save_mat[cbind(unbalancePred_ori_name, unbalanceTaxa_ori_name)] = -1000

    sig_ind = np.where((p_value_save_mat < fwerRate).to_numpy())
    sig_row = sig_ind[0]
    sig_col = sig_ind[1]

    est_sig = [
        est_save_mat.iloc[sig_row[my_i], sig_col[my_i]] for my_i in range(len(sig_row))
    ]
    CI_low_sig = [
        CI_low_mat.iloc[sig_row[my_i], sig_col[my_i]] for my_i in range(len(sig_row))
    ]
    CI_up_sig = [
        CI_up_mat.iloc[sig_row[my_i], sig_col[my_i]] for my_i in range(len(sig_row))
    ]
    p_adj_sig = [
        p_value_save_mat.iloc[sig_row[my_i], sig_col[my_i]]
        for my_i in range(len(sig_row))
    ]
    se_sig = [se_mat.iloc[sig_row[my_i], sig_col[my_i]] for my_i in range(len(sig_row))]

    est_sig = np.array(est_sig)
    CI_low_sig = np.array(CI_low_sig)
    CI_up_sig = np.array(CI_up_sig)
    p_adj_sig = np.array(p_adj_sig)
    se_sig = np.array(se_sig)

    cov_sig_index = np.sort(np.unique(sig_row))

    sig_list_each = {}

    if len(cov_sig_index) > 0:
        for iii in range(len(cov_sig_index)):
            sig_loc = which(sig_row == cov_sig_index[iii]).astype(int)
            est_spe_cov = est_sig[sig_loc]
            CI_low_spe_cov = CI_low_sig[sig_loc]
            CI_up_spe_cov = CI_up_sig[sig_loc]
            p_adj_spe_cov = p_adj_sig[sig_loc]
            se_spe_cov = se_sig[sig_loc]

            cov_sig_mat = np.zeros((len(sig_loc), 5))
            cov_sig_mat = pd.DataFrame(
                cov_sig_mat,
                columns=["estimate", "SE est", "CI low", "CI up", "adj p-value"],
            )
            cov_sig_mat.iloc[:, 0] = est_spe_cov
            cov_sig_mat.iloc[:, 1] = se_spe_cov
            cov_sig_mat.iloc[:, 2] = CI_low_spe_cov
            cov_sig_mat.iloc[:, 3] = CI_up_spe_cov
            cov_sig_mat.iloc[:, 4] = p_adj_spe_cov

            cov_sig_mat.index = colname_use[sig_col[sig_loc]]
            sig_list_each[testCovInOrder[cov_sig_index[iii]]] = cov_sig_mat

    all_cov_list["est_save_mat"] = est_save_mat
    all_cov_list["p_value_save_mat"] = p_value_save_mat
    all_cov_list["CI_low_mat"] = CI_low_mat
    all_cov_list["CI_up_mat"] = CI_up_mat
    all_cov_list["se_mat"] = se_mat

    results["sig_list_each"] = sig_list_each
    results["all_cov_list"] = all_cov_list

    return results


def runBootLassoHDCI(
    x,
    y,
    paraJobs,
    sequentialRun,
    bootB,
    bootLassoAlpha,
    seed,
    nfolds=10,
    lambdaOPT=np.empty(0),
    zeroSDCut=10 ** (-20) #,
    #correCut=0.996,
):
    results = {}
    nBeta = x.shape[1]
    nObsAll = len(y)

    # mask = np.ones(x.shape[1], dtype=bool)
    # # denote linear dependent columns
    # ld_col = detectLDcol(x)
    # mask[ld_col] = False
    # # denote constant columns
    # cons_col = detectCcol(x)
    # mask[cons_col] = False
    # xWithNearZeroSd = np.sort(
    #     np.unique(np.hstack((ld_col, cons_col))))

    # remove near constant x columns
    sdX = np.std(x, axis=0, ddof=1)
    xWithNearZeroSd = which(sdX <= zeroSDCut)

    # ChangePoint Cor
    # df_cor = np.corrcoef(x, rowvar=False)
    # excluCorColumns = which(
    #     np.apply_along_axis(
    #         lambda x: np.any(np.abs(x) >= correCut), 0, np.tril(df_cor, -1)
    #     )
    # )
    
    xWithNearZeroSd = np.sort(np.unique(np.hstack((xWithNearZeroSd))))  #, excluCorColumns))))

    if len(xWithNearZeroSd) > 0:
        x = np.delete(x, xWithNearZeroSd, axis=1)

    nearZeroSd = len(xWithNearZeroSd)

    # Bootstrap
    bootResu = bootLassoCI(
        x.copy(),
        y.copy(),
        seed=seed,
        sequentialRun=sequentialRun,
        paraJobs=paraJobs,
        bootLassoAlpha=bootLassoAlpha,
        bootB=bootB,
        nfolds=nfolds,
    )

    beta_LPR = bootResu["Beta_LPR"][:, 0]
    betaCI_LPR = bootResu["interval_LPR"]

    # transform vector back
    if len(xWithNearZeroSd) > 0:
        betaTransLasso_L = groupBetaToFullBeta(
            nTaxa=nBeta,
            nPredics=1,
            unSelectList=np.sort(xWithNearZeroSd),
            newBetaNoInt=beta_LPR,
        )

        beta_LPR = betaTransLasso_L["finalBeta"]

        betaTransCIlow_L = groupBetaToFullBeta(
            nTaxa=nBeta,
            nPredics=1,
            unSelectList=np.sort(xWithNearZeroSd),
            newBetaNoInt=betaCI_LPR[:, 0],
        )
        betaCIlow_LPR = betaTransCIlow_L["finalBeta"]

        betaTransCIhi_L = groupBetaToFullBeta(
            nTaxa=nBeta,
            nPredics=1,
            unSelectList=np.sort(xWithNearZeroSd),
            newBetaNoInt=betaCI_LPR[:, 1],
        )
        betaCIhi_LPR = betaTransCIhi_L["finalBeta"]
    else:
        betaCIlow_LPR = betaCI_LPR[:, 0]
        betaCIhi_LPR = betaCI_LPR[:, 1]

    results["Beta_LPR"] = beta_LPR
    results["interval_LPR"] = np.vstack((betaCIlow_LPR, betaCIhi_LPR))

    return results


def bootLassoCI(
    x,
    y,
    seed,
    paraJobs,
    bootLassoAlpha,
    sequentialRun=False,
    standardize=False,
    nfolds=10,
    nLam=100,
    intercept=True,
    bootB=50,
):

    results = {}
    alpha = 1  # lasso

    # ChangePoint Remove LD columns and constant columns

    np.random.seed(seed)
    scipy.random.seed(seed)
    foldid = np.random.choice(int(nfolds), int(len(y)), replace=True)

    cvResul = cvglmnet(
        x=x.copy(),
        y=y.copy(),
        alpha=alpha,
        nlambda=nLam,
        standardize=standardize,
        intr=intercept,
        foldid=foldid,
    )

    results["Beta_LPR"] = cvglmnetCoef(cvResul, s="lambda_min")[1:]

    bootLassoCIUnit_partial = partial(
        bootLassoCIUnit,
        x,
        y,
        alpha,
        cvResul["lambda_min"],
        standardize,
        intercept,
        seed,
    )

    if not sequentialRun:
        with tqdm_joblib(tqdm(desc="Phase2-Par", total=bootB)) as progress_bar:
            bootRunList = Parallel(n_jobs=int(paraJobs))(
                delayed(bootLassoCIUnit_partial)(i) for i in range(bootB)
            )

    if sequentialRun:
        bootRunList = [
            bootLassoCIUnit_partial(i) for i in tqdm(range(bootB), desc="Phase2-Seq")
        ]

    bootRunStack = np.hstack(bootRunList)
    bootCI = np.apply_along_axis(
        lambda xx: np.hstack(
            (
                np.quantile(xx, bootLassoAlpha / 2),
                np.quantile(xx, 1 - bootLassoAlpha / 2),
            )
        ),
        axis=1,
        arr=bootRunStack,
    )

    results["interval_LPR"] = bootCI

    return results


def bootLassoCIUnit(x, y, alpha, optimalLam, standardize, intercept, seed, i):

    np.random.seed(seed + i)
    scipy.random.seed(seed + i)

    rowToKeep = np.random.choice(len(y), len(y), replace=True)
    xBoot = x[rowToKeep, :]
    yBoot = y[rowToKeep]

    bootFit = glmnet(
        x=xBoot, y=yBoot, alpha=alpha, standardize=standardize, intr=intercept
    )

    return glmnetCoef(bootFit, s=scipy.float64([optimalLam]))[:, 0][1:]


# =============================================================================
# Help Functions
# =============================================================================


def colnames(x):
    if not isinstance(x, pd.core.frame.DataFrame):
        raise Exception("Input is not pandas.core.frame.DataFrame ")
    return x.columns.to_numpy(dtype="U")


def ncol(x):
    if not isinstance(x, pd.core.frame.DataFrame):
        raise Exception("Input is not pandas.core.frame.DataFrame ")
    return len(x.columns)


def nrow(x):
    if not isinstance(x, pd.core.frame.DataFrame):
        raise Exception("Input is not pandas.core.frame.DataFrame ")
    return len(x.index)


def colSums(x):
    if not isinstance(x, pd.core.frame.DataFrame):
        raise Exception("Input is not pandas.core.frame.DataFrame ")
    return x.sum(axis=0)


def rowSums(x):
    if not isinstance(x, pd.core.frame.DataFrame):
        raise Exception("Input is not pandas.core.frame.DataFrame ")
    return x.sum(axis=1)


def r_in(x, y):
    x, y = np.array(x), np.array(y)
    return np.array([np.isin(item, y) for item in x]).astype(bool)


def r_ni(x, y):
    x, y = np.array(x), np.array(y)
    return np.array([not np.isin(item, y) for item in x]).astype(bool)


def rm(*args):
    del args


def inv_bool(x):
    return [not i for i in x]


def cbind(x):
    return pd.concat(x, axis=1)


def which(x):
    return np.array([i for i, j in enumerate(x) if j], dtype=int)


def np_assign_but(ar, but_ind, v):
    assign_ind = np.setdiff1d(np.arange(len(ar)), but_ind)
    ar[assign_ind] = v
    return


@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """Context manager to patch joblib to report into tqdm progress bar given as argument"""

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


def calculate_se(bootLassoAlpha, x):
    return np.abs(x[1] - x[0]) / (2 * scipy.stats.norm.ppf(1 - bootLassoAlpha / 2))


# =============================================================================
# Help Functions
# =============================================================================
