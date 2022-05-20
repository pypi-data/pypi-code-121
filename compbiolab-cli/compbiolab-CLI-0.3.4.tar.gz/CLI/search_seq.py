import sys
import argparse
from .SearchSQOutput import SearchSQOutput
from .output_results import output_result


def seq_search(args: argparse.Namespace):
    """

    Parameters
    ----------
    args : argparse.Namespace
    """
    if sys.version_info[:2] == (3, 7) and ('32 bit' not in sys.version):
        # don't import function and dependencies if you don't need to
        try:
            from .SearchSQ import SearchSQ
            ns: str
            for ns in args.sequence:
                res: SearchSQOutput = SearchSQ(ns).result
                output_result(res, args.output_file, args.output_format, args.output_mode)
        except Exception as err:
            print("Error")
            exit(err)

    else:
        print("Sequence searches only supported on 64-bit Python 3.7")
