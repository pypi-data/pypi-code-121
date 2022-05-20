import argparse
from argparse_formatter import FlexiFormatter
from .search_seq import seq_search
from .family_list import print_families
from .search_lat import ls_search
from . import output_opt_parser, dist_opt_parser


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='''Find the closest protein family to a new latent space or protein sequence. 
    
Available metrics: 
    euclidean, minkowski, cityblock, sqeuclidean, cosine, correlation, hamming, jaccard, chebyshev, canberra, braycurtis, yule, dice, kulsinski, rogerstanimoto, russellrao, sokalmichener, sokalsneath

To see all the available protein families, run command:
    search names
            
Or you can find the closest protein family to first_new_latent_example.txt in cosine distance by running the command:
    search lat first_new_latent_example.txt -m cosine

Also you can find the closest family to a new protein sequence (for example new_sequence_example.txt) by running:
    search seq new_sequence_example.txt
    
    ''',
                                                              formatter_class=FlexiFormatter)
    subparsers = parser.add_subparsers(dest='command')
    parser_ls: argparse.ArgumentParser = subparsers.add_parser('lat', help="Provide a new protein family latent space. The closest protein family to this new latent space will be shown.", parents=[
        output_opt_parser, dist_opt_parser])
    parser_ls.add_argument('latent_space', metavar="filename", help="The file name of a new latent space.", type=str, nargs='+')

    parser_seq: argparse.ArgumentParser = subparsers.add_parser('seq', help="Provide a protein sequence to get the closest protein family for this sequence.", parents=[
        output_opt_parser])
    parser_seq.add_argument('sequence', metavar="filename", help="The name of the file containing a protein sequence.", type=str, nargs='+')

    parser_names: argparse.ArgumentParser = subparsers.add_parser('names', help="Show available protein family names")

    parser_ls.set_defaults(func=ls_search)
    parser_seq.set_defaults(func=seq_search)
    parser_names.set_defaults(func=print_families)
    args: argparse.Namespace = parser.parse_args()
    # print help text if nothing is selected
    if args.command is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
