# File Name: old_samples.py
# Created By: ZW
# Created On: 2022-05-27
# Purpose: defines dataclass objects for samples and a function for generating
# sample sets from .fam, pheno, and sample-subset files.

# Module Imports
# ----------------------------------------------------------------------------
from dataclasses import dataclass, field
from re import split
from typing import Union
from sys import getsizeof, stderr


# Exception Definitions
# ----------------------------------------------------------------------------

# define a base class for exceptions relating to Sample proccessing or operations
class SampleException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__()
        self.message = message

    # define __str__() internal string representation of the exception(the error message)
    def __str__(self):
        return f"{self.message}"

    # define test_message() external function to print the error message to
    # stderr without raising the actual error
    def test_message(self):
        self._stderr_print(self.__str__())

    # define _stderr_print internal method that prints to stderr
    @staticmethod
    def _stderr_print(*args, **kw):
        print(*args, file=stderr, **kw)


# Alias more specific exception names from the base class
# error raised when covariates table dimensions can't be coerced
# into the loaded samples sensibly
class SampleCovariatesDimensionError(SampleException):
    def __init__(self, message):
        super(SampleException, self).__init__()
        self.message = message


# error raised when a sample object is compared to a non-sample object
class SampleComparisonError(SampleException):
    def __init__(self, message):
        super(SampleException, self).__init__()
        self.message = message


# Function Definitions
# ----------------------------------------------------------------------------

# define a function that checks if a tuple of (family id, individual id) is in another
# list of tuples of the same format representing the subset of the samples to keep
def verify_sample_id(to_check, subset_list):
    if not subset_list:
        return True
    else:
        return True if to_check in subset_list else False


# define a function that translates plink format case-control values to unambiguous
# strings (2 - case, 1 - control)
def resolve_plink_cc(pheno_value):
    return "case" if pheno_value == 1 else "control"


# define a function read_sample_data() which takes a number of files and
# creates a list of samples for which their attributes (including their
# phenotype information and covariate information can be stored
def read_sample_data(fam_path, sample_subsets_path, covars_path, pheno_fmt):
    samples_out = []  # stores output list of samples read from files
    subset_ids = []  # stores the fids and iids of a subset of the .fam file
    covars_list = []  # stores the covariates passed by the covars file
    covars_names = []  # stores the names of covariates passed by the covars file
    fam_data = []  # stores .fam data before its converted to sample objs

    # collect sample subsets if passed
    if sample_subsets_path:
        print("Reading sample subset file..")
        with open(sample_subsets_path, 'r') as fobj:
            for line in fobj:
                fid, iid = split(r"\s+", line.strip())
                subset_ids.append((fid, iid))

    # collect covariates data
    if covars_path:
        print("Reading covariates file..")
        with open(covars_path, 'r') as fobj:
            for line in fobj:
                text = line.strip()
                if len(text) > 0:
                    covars_list.append(tuple(split(r"\s+", text)))
        covars_names = covars_list.pop(0)

    # collect sample data from .fam file
    print("Reading .fam file..")
    with open(fam_path, 'r') as fobj:
        for line in fobj:
            fam_data.append(tuple(split(r"\s+", line.strip())))

    # construct sample objects
    print("Integrating sample information..")
    covar_indices_to_remove = []
    for pos, sdat in enumerate(fam_data):
        if verify_sample_id(sdat[:2], subset_ids):
            pheno = resolve_plink_cc(sdat[-1]) if pheno_fmt == "cc" else sdat[-1]
            samples_out.append(Sample(*sdat[:-1], phenotype=pheno,
                                      covariates={}, gt_position=pos))
        else:
            covar_indices_to_remove.append(pos)  # remove the index from covar indices list if we skip it
            continue
    covar_indices_to_remove.reverse()
    covar_indices = list(range(len(fam_data)))
    [covar_indices.pop(c) for c in covar_indices_to_remove]

    # add covariates if they are present
    if covars_path:
        # check if covariates were supplied for everyone in .fam and theres no subset
        if (not sample_subsets_path) and (len(covars_list) == len(fam_data)):
            for pos, covars in enumerate(covars_list):
                samples_out[pos].covariates = dict(zip(covars_names, covars))

        # check if covariates were supplied for everyone in .fam and there is a subset
        elif sample_subsets_path and (len(covars_list) == len(fam_data)):
            covar_subset = [covars_list[i] for i in covar_indices]
            for pos, covars in enumerate(covar_subset):
                samples_out[pos].covariates = dict(zip(covars_names, covars))

        # check if covariates were supplied only for the supplied subset
        elif sample_subsets_path and (len(covars_list) == len(subset_ids)):
            for pos, covars in enumerate(covars_list):
                samples_out[pos].covariates = dict(zip(covars_names, covars))
        else:
            fam_len = len(fam_data)
            subset_len = len(subset_ids)
            covars_len = len(covars_list)
            msg = f"""
                Covariates file dimension does not match .Fam and/or sample subset.
                Number of samples in .fam file: {fam_len}
                Number of samples in sample subset file: {subset_len}
                Number of covariate observations in covars file: {covars_len}
            """
            raise SampleCovariatesDimensionError(msg)

    # return the list of Sample objects we've generated
    num_samples = len(samples_out)
    mb_used = float(getsizeof(samples_out)) / 10**6
    print(f"Processed and loaded {num_samples} samples from input files -- in {mb_used} MB of memory\n")
    return sorted(samples_out)

# Class Definitions
# ----------------------------------------------------------------------------


# define a dataclass for each individual called Sample which holds its
# identifying information, genotyping position in bed file, and phenotypes
@dataclass
class Sample:
    fid: str  # family id
    iid: str  # within-family (individual) id
    paternal_iid: str  # within-family id of father
    maternal_iid: str  # within-family id of mother
    asserted_sex: int  # sex code provided in the fam file
    phenotype: Union[str, float]  # the phenotype from the .fam file
    covariates: field(default_factory=dict)  # dictionary to contain covars
    gt_position: int  # row position in .fam file and order in each .bed block

    # define __eq__ internal method based on all of the sample attributes
    def __eq__(self, other):
        if isinstance(other, Sample):
            same = (self.__dict__ == other.__dict__)
            return True if same else False
        else:
            other_type = type(other)
            msg = f"""
                Cannot Compare object of type {other_type} to Sample Object 
            """
            raise SampleComparisonError(msg) from TypeError

    # define __lt__ internal method based on the gt_position alone
    def __lt__(self, other):
        if isinstance(other, Sample):
            less = (self.gt_position < other.gt_position)
            return True if less else False
        else:
            other_type = type(other)
            msg = f"""
                Cannot Compare object of type {other_type} to Sample Object 
            """
            raise SampleComparisonError(msg) from TypeError

    # define __gt__ internal method based on the gt_position alone
    def __gt__(self, other):
        if isinstance(other, Sample):
            greater = (self.gt_position > other.gt_position)
            return True if greater else False
        else:
            other_type = type(other)
            msg = f"""
                Cannot Compare object of type {other_type} to Sample Object 
            """
            raise SampleComparisonError(msg) from TypeError

    # define __le__ internal method based on the gt_position alone
    def __le__(self, other):
        tests = (self.__lt__(other), self.__eq__(other))
        return True if any(tests) else False

    # define __ge__ internal method based on the gt_position alone
    def __ge__(self, other):
        tests = (self.__gt__(other), self.__eq__(other))
        return True if any(tests) else False
