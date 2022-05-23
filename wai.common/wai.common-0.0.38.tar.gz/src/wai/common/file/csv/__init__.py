"""
Package for reading and representing CSV files.

Typical usage:
from wai.common.file.csv import loadf
file: CSVFile = loadf('filename.csv')
process_csv_file(file)
"""
from ._CSVFile import CSVFile
from ._load import load, loadf, loads
from ._save import save
