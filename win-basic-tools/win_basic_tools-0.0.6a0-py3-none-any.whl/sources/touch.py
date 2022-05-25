import os
import sys

if len(sys.argv) >= 2:
    for i in sys.argv[1:]:
        os.system(f'type nul > {i}')
else:
    print('Pass parameters for creating files. E.g. touch file.py file2.pyw')
