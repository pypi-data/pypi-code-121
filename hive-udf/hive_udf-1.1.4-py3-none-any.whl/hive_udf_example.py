'''
This is an example UDF for Hive, to be processed by `make_udf` and used in tests.

UDFs should follow this example. The main points include:

1. The code in this module is written against the Python version that is
   available on the Hive cluster.

2. Because this module runs in the environment on the server (worker nodes
   to be precise), only packages in the server's environment can be used.
   To be safe, it's a good idea to make this module *self sufficient* and use
   Python's standard libraries only. It should not use disk files.

3. This example defines a main function that processes a single line,
   and the entry block passes individual lines on stdin to this function.
   This is a reasonable pattern to use.

   However, if you have an existing UDF script that works but does not
   follow this pattern, it is not necessary to modify the script.
   It is expected that `make_udf` 'just works'.

4. `from __future__ import print_function` is recommended.
   If this module is written against Python 2, but this module needs
   to be imported into Python 3 code, then this import is required.

What this UDF does:

Take two columns: `id`, `info_json`.
Parse `info_json` to get `make` and `price`.
Print out these two columns.
If `price` does not exist in `make`, that column is NULL.
'''

from __future__ import print_function
import json
import sys

SEP = '\t'
NULL = '\\N'


def main():
    for line in sys.stdin:
        _, info_json = line.strip().split(SEP)
        info = json.loads(info_json)
        print(info['make'] + SEP + str(info.get('price', NULL)))


if __name__ == '__main__':
    main()
