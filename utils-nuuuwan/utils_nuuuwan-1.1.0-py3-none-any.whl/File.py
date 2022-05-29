import csv
import json

DIALECT = 'excel'
DELIMITER_CSV = ','
DELIMITER_TSV = '\t'


class File:
    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        with open(self.file_name, 'r') as fin:
            content = fin.read()
            fin.close()
        return content

    def write(self, content):
        with open(self.file_name, 'w') as fout:
            fout.write(content)
            fout.close()

    def read_lines(self):
        return File.read(self).split('\n')


class JSONFile(File):
    def read(self):
        content = File.read(self)
        return json.loads(content)

    def write(self, data):
        content = json.dumps(data, indent=2)
        File.write(self, content)


class XSVFile(File):
    def __init__(self, file_name, delimiter):
        File.__init__(self, file_name)
        self.delimiter = delimiter

    def read(self):
        csv_lines = File.read_lines(self)

        data_list = []
        field_names = None
        reader = csv.reader(
            csv_lines,
            dialect=DIALECT,
            delimiter=self.delimiter,
        )
        for row in reader:
            if not field_names:
                field_names = row
            else:
                data = dict(
                    zip(
                        field_names,
                        row,
                    )
                )
                if data:
                    data_list.append(data)
        return data_list

    def write(self, data_list):
        with open(self.file_name, 'w') as fout:
            writer = csv.writer(
                fout,
                dialect=DIALECT,
                delimiter=self.delimiter,
            )

            field_names = list(data_list[0].keys())
            writer.writerow(field_names)
            writer.writerows(
                list(
                    map(
                        lambda data: list(
                            map(
                                lambda field_name: data[field_name],
                                field_names,
                            )
                        ),
                        data_list,
                    )
                ),
            )
            fout.close()


class CSVFile(XSVFile):
    def __init__(self, file_name):
        return XSVFile.__init__(self, file_name, DELIMITER_CSV)


class TSVFile(XSVFile):
    def __init__(self, file_name):
        return XSVFile.__init__(self, file_name, DELIMITER_TSV)
