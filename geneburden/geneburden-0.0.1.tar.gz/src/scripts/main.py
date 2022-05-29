# File Name: main.py
# Created By: ZW
# Created On: 2022-05-32
# Purpose: main commandline entry-point for burden testing application
# handles all of the I/O operations between program and user.

# Module Imports
# ----------------------------------------------------------------------------
import argparse
from pathlib import Path
from geneburden.samples import read_sample_data
from geneburden.features import read_intervals_data

# Function Definitions
# ----------------------------------------------------------------------------


# define a function resolve_path() which checks that (1) the passed file exists
# (2) that it has the proper extension is specified
def resolve_path(path_string, allowed_extensions=None):
    path = Path(path_string)
    if path.exists():
        if not allowed_extensions: # no specified extension constraints
            return path
        elif allowed_extensions and (path.suffix in allowed_extensions):
            return path
        else:
            msg = f"""
                {path_string} has unacceptable file extension- {path.suffix}.
                Allowed file extensions for this argument: {allowed_extensions}.
            """
            raise Exception(msg)
    else:
        raise FileNotFoundError(f"{path_string} Does not seem to exist.")


# define function main() which serves as the entry point for the burden
# test application-- acts as the commandline argument parser and controller
def main():
    # ------------------------------------------------------------------------
    # specify command line arguments, and parse them from the user.

    # multi-line tool description TODO: complete tool description
    description = """
        Geneburden: A tool for testing variant burdens over specific genomic intervals
        in case-control cohorts. (Copyright ZW- 2022) 
    """
    # format commandline parser
    parser = argparse.ArgumentParser(description)
    parser.add_argument("--bfile", type=str, help="file naming conventions for .bim/.fam/.bed genotype files")
    parser.add_argument("--covars", type=str, help="text file containing covariates")
    parser.add_argument("--samples", type=str, help="text file containing family and individual ids to include")
    parser.add_argument("--pheno-name", type=str, help="name of phenotype found in the .fam file")
    parser.add_argument("--pheno-fmt", choices=["cc", "quant"],
                        help="indicate if the pheno is case-control or quantitative")
    parser.add_argument("test", choices=["permutation", "linear"],
                        help="Specify the type of enrichment test to employ")
    parser.add_argument("features", type=str, help="UCSC .bed (BED6+) or .gtf formatted features")
    args = parser.parse_args()

    # print the arguments specified by the commandline input
    print(description + "\n\tPassed Arguments:")
    print("\t-----------------")
    for arg in vars(args):
        print(f"\t{arg}: -->  {getattr(args,arg)}")
    print("", end="\n") # formatting print

    # instantiate given file paths into pathlib.Path objects and verify that they exist
    # instatntiate required paths:
    bed_path = resolve_path(args.bfile + ".bed", [".bed"])
    bim_path = resolve_path(args.bfile + ".bim", [".bim"])
    fam_path = resolve_path(args.bfile + ".fam", [".fam"])
    covars_path = resolve_path(args.covars, None)
    features_path = resolve_path(args.features, [".bed", ".gtf"])

    # instantiate optional paths if they were passed:
    samples_path = resolve_path(args.samples, None) if args.samples else None

    # grab other passed variable names
    pheno_name = args.pheno_name
    pheno_fmt = args.pheno_fmt

    # ------------------------------------------------------------------------
    # process the inputs for the samples, genome_features, variants, and genotypes in that order
    # process the .fam and covariates files, extract and filter based on sample subset file
    samples = read_sample_data(fam_path, samples_path, covars_path, pheno_fmt)
    features = read_intervals_data(features_path, features_path.suffix)

    print("\n")
    print(samples[:5])
    print(features[:5])

    # end the program
    exit(0)
