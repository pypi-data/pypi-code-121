import csv


def get_template(path: str, delimiter: str = ';'):
    with open(path, newline='') as f:
        readed_data = csv.reader(f, delimiter=delimiter)
        data: list = [row for row in readed_data]
    return data
