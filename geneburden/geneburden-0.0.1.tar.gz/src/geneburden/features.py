# Created By: ZW
# Created On: 2022-05-29
# Purpose: defines dataclass objects for genomic features and a function reading
# in feature data from both interval type files (.bed, .gtf) and plink style .bim files for variants

# Module Imports
# ----------------------------------------------------------------------------
from dataclasses import dataclass, field
from re import split
from sys import getsizeof, stderr
# TODO cleanup module imports if we don't use all of these classes


# Exception Definitions
# ----------------------------------------------------------------------------

# define a base class for exceptions relating to GenomeFeature proccessing or operations
class GenomeFeatureException(Exception):
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
# error raised when a GenomeFeature type object is compared to a GF object
class FeatureComparisonError(GenomeFeatureException):
    def __init__(self, message):
        super(GenomeFeatureException, self).__init__()
        self.message = message


# error raised when a file containing GenomeFeatures has the wrong extension
class FeatureFileExtensionError(GenomeFeatureException):
    def __init__(self, message):
        super(GenomeFeatureException, self).__init__()
        self.message = message


# error raised when a file containing GenomeFeatures is malformed, and cannot be parsed
class FeatureFileParsingError(GenomeFeatureException):
    def __init__(self, message):
        super(GenomeFeatureException, self).__init__()
        self.message = message


# Function Definitions
# ----------------------------------------------------------------------------

# define function for reading in genomic features data from .bed or .gtf
# IMPORTANT: all features are converted to 1-indexed [start,end] closed intervals which are
# standard practice for .gtf files and not standard practice for BED files which are
# conventionally 0-indexed [start,end) semi-open intervals. BED format intervals
# are converted to [(start + 1), end] for a starndard data representation.
def read_intervals_data(intervals_path, intervals_type):
    intervals_out = []  # list of GenomeFeatures objects from intervals to return
    with open(intervals_path, 'r') as fobj:
        if intervals_type == ".bed":  # handle .bed (UCSC- not plink) files
            print("Reading genome features from UCSC .bed file..")
            for line in fobj:
                try:
                    contig, start, stop, name, *_etc = line.strip().split("\t")
                    intervals_out.append(
                        GenomeFeature(feat_id=name, contig=contig, pos_start=(int(start)+1), pos_end=int(stop))
                    )
                except Exception as e:
                    msg = f"""
                        Could Not parse passed intervals data. 
                        File likely malformed or incorrectly formated.
                        offending file: {intervals_path}
                        offending line: {line}
                    """
                    raise FeatureFileParsingError(msg) from e

    # TODO implement read_intervals_data subroutine for .gtf files
        elif intervals_type == ".gtf":  # handle .gtf files
            print("Reading genome features from .gtf file..")
            pass
        else:
            msg = f"""
                File path or Path object passed to read_intervals_data() appears to have wrong extension.
                Passed File: {intervals_path}
                allowed formats: .bed (UCSC -not plink) and .gtf
            """
            raise FeatureFileExtensionError(msg)

    # return the list of sorted intervals
    num_intervals = len(intervals_out)
    mb_used = float(getsizeof(intervals_out)) / 10**6
    print(f"Processed and loaded {num_intervals} genome features from input files -- in {mb_used} MB of memory\n")
    return sorted(intervals_out)


# define function for reading in variants from .bim file
def read_variant_data(variants_path):
    return None  # TODO implement read_variant_data funciton


# Class Definitions
# ----------------------------------------------------------------------------

# defines GenomeFeature() a base class for all genome features which contains its
# unique id, positional information, and annotations.
# IMPORTANT: all features are converted to 1-indexed [start,end] closed intervals which are
# standard practice for .gtf files and not standard practice for BED files which are
# conventionally 0-indexed [start,end) semi-open intervals. BED format intervals
# are converted to [(start + 1), end] for a starndard data representation.
@dataclass(frozen=True, eq=False, order=False)
class GenomeFeature:
    feat_id: str  # stores a unique identifier for the feature
    contig: str  # stores the chromosome or scaffold on which the feature lies
    pos_start: int  # stores the coordinate (1-indexed) of the beginning of the feature
    pos_end: int  # stores the coordinate (1-indexed) of the end of the feature

    # define __eq__() equality operator based on genomic coordinates alone
    # to be considered equal the features must have the same start and end point
    def __eq__(self, other):
        if isinstance(other, GenomeFeature):
            # test that the intervals are positionally equivalent
            tests = ((self.pos_start == other.pos_start),
                     (self.pos_end == other.pos_end))
            return True if all(tests) else False
        else:  # raise error if the compared object is not a Genome Feature
            othertype = other.__class__
            msg = f"""
                Passed object is not of type GenomeFeature, type: {othertype} found\n
            """
            raise FeatureComparisonError(msg) from TypeError

    # define __lt__() internal less than operator based on genomic coordinates alone
    # to be considered less than the pos_start of self must be strictly less than the compared object
    def __lt__(self, other):
        if isinstance(other, GenomeFeature):
            tests = (self.pos_start < other.pos_start,)
            return True if all(tests) else False
        else:  # raise error if the compared object is not a Genome Feature
            othertype = other.__class__
            msg = f"""
                Passed object is not of type GenomeFeature, type: {othertype} found\n
            """
            raise FeatureComparisonError(msg) from TypeError

    # define __le__() internal less than or equal to operator
    # to be considered le, is the logical OR of lt, and eq
    def __le__(self, other):
        if isinstance(other, GenomeFeature):
            tests = (self.__lt__(other), self.__eq__(other))
            return True if all(tests) else False
        else:  # raise error if the compared object is not a Genome Feature
            othertype = other.__class__
            msg = f"""
                Passed object is not of type GenomeFeature, type: {othertype} found\n
            """
            raise FeatureComparisonError(msg) from TypeError

    # define __gt__() internal greater than operator based on genomic coordinates alone
    # to be considered greater than the pos_start of self must be strictly larger than the compared object
    def __gt__(self, other):
        if isinstance(other, GenomeFeature):
            tests = (self.pos_start > other.pos_start,)
            return True if all(tests) else False
        else:  # raise error if the compared object is not a Genome Feature
            othertype = other.__class__
            msg = f"""
                Passed object is not of type GenomeFeature, type: {othertype} found\n
            """
            raise FeatureComparisonError(msg) from TypeError

    # define __ge__() internal greater than or equal to operator
    # to be considered ge, is the logical OR of gt, and eq
    def __ge__(self, other):
        if isinstance(other, GenomeFeature):
            tests = (self.__gt__(other), self.__eq__(other))
            return True if all(tests) else False
        else:  # raise error if the compared object is not a Genome Feature
            othertype = other.__class__
            msg = f"""
                Passed object is not of type GenomeFeature, type: {othertype} found\n
            """
            raise FeatureComparisonError(msg) from TypeError


# defines GeneticVariant() a data class for genetic variant information. this data class only represents a single
# variant allele meaning that a bi-allelic site can be fully captured by one instance, but multi-allelic sites require
# n-1 instances for n possible alleles
@dataclass(frozen=True, eq=False, order=False)
class Variant(GenomeFeature):
    major_allele: str  # the string representation of the major allele
    minor_allele: str  # a string representation of the minor allele
    maf: float  # the population frequency of the minor allele
    annotations: dict = field(default_factory=dict)  # create a dictionary for feature annotations
