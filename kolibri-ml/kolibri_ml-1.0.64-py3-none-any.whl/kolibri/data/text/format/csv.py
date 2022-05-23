import csv


def read_csv(file_name, file_type='csv', separator=',', encoding='utf-8'):
    if file_type in ['csv', 'txt', 'tsv']:
        with open(file_name, encoding=encoding) as file:
            reader = csv.DictReader(file, delimiter=separator)
            for line in reader:
                yield line
    else:
        raise NotImplementedError("file type not yet supported")
