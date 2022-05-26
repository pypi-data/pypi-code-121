#!/usr/bin/env python
# coding: utf-8

from itertools import tee
import json
import argparse
import logging
from os import path

from cobra.io import read_sbml_model
from cobra.util import solvers

from csmemo.reachability import ReachabilityTester
from csmemo.consistency_analysis import get_unconnected_modules_frame


SOLVERS = list(solvers.keys())
if 'cglpk' in SOLVERS:
    SOLVERS.remove('cglpk')
    SOLVERS.append('glpk')

METHODS = ('lp7', 'fva')
DELETION_TYPES = ('gene', 'reaction')


def create_parser():
    parser = argparse.ArgumentParser(description='Run reachability analysis on genome-scale metabolic model.')

    parser.add_argument('sbml_fname', action="store", help='SBML file to use a the model reference')

    parser.add_argument('compounds_fname', action="store", help='JSON file storing the id of the metabolite to test')

    parser.add_argument('--type', action="store", dest="deletion_type", choices=DELETION_TYPES,
                        default='gene', help='Set the element type (gene/reaction) to test')

    parser.add_argument('--media', action="store", dest="json_exchanges", default=None,
                        help='JSON file storing the exchange bounds')

    parser.add_argument('--method', action="store", dest="method", choices=METHODS,
                        default='lp7', help='Optimization method to perform reachability')

    parser.add_argument('--solver', action="store", dest="solver", choices=SOLVERS,
                        default='glpk', help='LP solver to perform optimizations')

    parser.add_argument('--out', action="store", dest="output_folder", default=".",
                        help='Output folder to store the builded CSM')

    parser.add_argument('--verbose', action="store_true", dest="verbose", default=False,
                        help='Verbose mode')

    parser.add_argument('--find-ums', action="store_true", dest="find_ums", default=False,
                        help='Calculate unconnected modules set for blocked precursors')

    parser.add_argument('--save-square', action="store_true", dest="save_square", default=False,
                        help='Save the reachability matrix in dense form (rectangular matrix)')


    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO

    print("===================================================================")
    print("Reading sbml model: %s -->" % args.sbml_fname, end=" ")
    model = read_sbml_model(args.sbml_fname)
    model.solver = args.solver
    print("OK!")

    if args.json_exchanges:
        print("Reading media composition (json file): %s -->" % args.json_exchanges, end=" ")
        with open(args.json_exchanges) as fh:
            media_dict = json.load(fh)
            print("OK!")

        print("Setting media to model", end=" ")
        media_dict = {k: v for k, v in media_dict.items() if k in model.reactions}
        for r in model.exchanges:
            r.lower_bound = 0
            if r.id in media_dict:
                print(r.id)
                r.lower_bound = -1 * media_dict[r.id]

        print("OK!")

    print("Reading compound list (json file): %s -->" % args.compounds_fname, end=" ")
    with open(args.compounds_fname) as fh:
        all_compounds = json.load(fh)
    print("OK!")

    compounds_in_model = [i for i in all_compounds if i in model.metabolites]
    excluded_compounds = set(all_compounds) - set(compounds_in_model)

    reachability_tester = ReachabilityTester(model, compounds_in_model)
    default_not_produced = reachability_tester.run_reactions_reachability([])

    print("==========================================================================")
    print("- Initial set of biomass precursors to test: %i" % len(all_compounds))
    print("- Excluded compounds (not present in model) %i:" % len(excluded_compounds))
    print(" ".join(excluded_compounds))
    print("- Excluded compounds (not produced by model) %i:" % len(default_not_produced))
    print(" ".join(default_not_produced))
    print("- Total biomass precursors to be tested: %i" % len(compounds_in_model))
    print("==========================================================================")

    compounds_in_model = [i for i in compounds_in_model if i not in default_not_produced]



    reachability_tester = ReachabilityTester(model, compounds_in_model, level=level)

    print("Running single % reachability using method %s --> " % (args.deletion_type, args.method), end=" ")
    if args.deletion_type == 'gene':
        df_reachability = reachability_tester.single_gene_reachability(method=args.method)

    elif args.deletion_type == 'reaction':
        df_reachability = reachability_tester.single_reaction_reachability(method=args.method)

    print("OK!")

    column_id = args.deletion_type + "_id"
    elements = df_reachability[column_id].unique()

    compound_col = "compound_id"
    compounds = df_reachability[compound_col].unique()
    print("===================================================================")
    print("- %s disabling compound biosynthesis %i:" % (args.deletion_type, len(elements)))
    print(" ".join(sorted(elements)))
    print("- Compound no reached by at least one %s knockout %i:" % (args.deletion_type,len(compounds)))
    print(" ".join(sorted(compounds)))
    print("===================================================================")

    df_unconnected_modules = None
    if args.find_ums:
        print("Calculating unconnected_modules", end=" ")
        df_unconnected_modules = get_unconnected_modules_frame(model, elements, element_type=args.deletion_type)
        print("OK!")

    fname = path.join(args.output_folder, "single_" + args.deletion_type + "_reachability_" + model.id + ".tsv")
    print("Saving reachability frame to %s" % fname)
    df_reachability.to_csv(fname, sep='\t')
    
    if args.save_square:
        print("Saving reachability square frame to %s" % fname)
        fname = path.join(args.output_folder, "single_" + args.deletion_type + "_reachability_square_" + model.id + ".tsv")
        df_reachability_square = reachability_tester.to_square_form(df_reachability)
        df_reachability_square.to_csv(fname, sep='\t')

    if df_unconnected_modules is not None:
        fname = path.join(args.output_folder, "single_" + args.deletion_type + "_reachability_" + model.id + ".tsv")
        print("Saving reachability unconnected modules frame to %s" % fname)
        df_unconnected_modules.to_csv(fname, sep='\t')



if __name__ == "__main__":
    main()

