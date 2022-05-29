import argparse

from .__dip import dip_this_func


par = argparse.ArgumentParser()
par.add_argument(
    "number",
    type=str,
    help="Number to convert, (This number is assumed to be in base 10 if --current_base is not provided)"
)
par.add_argument("new_base", type=int, help="Base to convert the number to")
par.add_argument(
    "--current_base",
    "-cb",
    type=int,
    default=10,
    help="Base of the number currently, default is 10 if none is provided"
)
args = par.parse_args()

dip_this_func(args.number, args.new_base, args.current_base)
