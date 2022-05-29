'''
This is an example UDAF for Hive, to be processed by `make_udf` and used in tests.

Reference:
    https://florianwilhelm.info/2016/10/python_udf_in_hive/


What this UDAF does:


Take two columns: `id`, `info_json`.
Parse `info_json` to get `make` and `price`.
Print out these two columns.

Two parameters control further details:

The first parameter is `country`, with possible values 'all', 'jap', 'america'.
Only records with car maker in the specified country are processed.

The second parameter is 'default price'. If `info_json` does not contain price,
use this default value.
'''

from __future__ import print_function
import json
import sys


SEP = '\t'
NULL = '\\N'


MAKES = {
    'jap': ['honda'],
    'america': ['ford', 'tesla']
}


def main(country, price_default):
    for line in sys.stdin:
        _, info_json = line.strip().split(SEP)
        info = json.loads(info_json)
        make = info['make']
        price = info.get('price', price_default)
        if country == 'all' or make in MAKES[country]:
            print(make + SEP + str(price))


if __name__ == '__main__':
    # Note: due to the way `make_udf` handles this script,
    # the parameters should be retrieved as `sys.argv[2]`
    # and `sys.argv[3]`, etc.

    country = sys.argv[2]
    price_default = float(sys.argv[3])

    # In reality this error situation should be handled in a better way.
    assert country == 'all' or country in MAKES

    main(country, price_default)
