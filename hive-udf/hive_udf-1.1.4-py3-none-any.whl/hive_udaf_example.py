'''
This is an example UDAF for Hive, to be processed by `make_udf` and used in tests.

What this UDAF does:

Take a single column `info_json`, which is `clustered`
by the `make` element in the JSON (i.e. records of the same `make`
come consecutively to the same Hive worker node),
parse this JSON to get `make` and `price`.
For each `make`, calculate average price of the records that have `price`;
also count the records that lack `price`.
Print out three columns:

    `make`, `average_price`, `number_of_null_price`

Since this UDAF requires the records to be already clustered by `make`,
the caller necessarily needs to extract `make` from `info_json` and use it.
So, the caller may as well provide two columns: `make` and `info_json`.
That would simplify this UDAF a little bit.

Here we assume the caller does not provide that convenience.
'''

from __future__ import print_function
import itertools
import json
import sys


SEP = '\t'
NULL = '\\N'


def read_data(input_data=sys.stdin):
    for line in input_data:
        info = json.loads(line.strip())
        yield info['make'], info.get('price', NULL)


def main():
    data = read_data()
    for make, group in itertools.groupby(data, lambda x: x[0]):
        n_good = 0
        n_bad = 0
        price_sum = 0
        for _, price in group:
            if price == NULL:
                n_bad += 1
            else:
                p = float(price)
                # In reality one may want to handle possible error here.
                # Here we assume this will not fail.

                price_sum += p
                n_good += 1
        avg_price = round(price_sum / n_good)
        print(make + SEP + str(avg_price) + SEP + str(n_bad))


if __name__ == '__main__':
    main()
