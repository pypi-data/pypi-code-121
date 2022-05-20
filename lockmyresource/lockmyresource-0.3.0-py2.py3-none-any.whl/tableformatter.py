import abc
import csv
import io
import json
from typing import Dict, List


class TableFormatter(abc.ABC):
    TEXT = "text"
    CSV = "csv"
    FORMAT_JSON = "json"

    @abc.abstractmethod
    def to_string(self, rows) -> str:
        pass

    @staticmethod
    def create(table_format: str):
        if table_format == TableFormatter.TEXT:
            return TextFormatter()
        if table_format == TableFormatter.CSV:
            return CsvFormatter()
        if table_format == TableFormatter.FORMAT_JSON:
            return JsonFormatter()
        raise KeyError(table_format)


class TextFormatter(TableFormatter):
    def to_string(self, rows) -> str:
        columns = "resource user locked_at comment".split()
        header = {key: key.capitalize() for key in columns}
        rows.insert(0, header)

        column_lengths = {
            key: max([len(str(row[key])) for row in rows]) for key in rows[0].keys()
        }

        def format_cell(column, value):
            template = f"{{value:{column_lengths[column]}}}"
            return template.format(value=str(value))

        def format_row(row):
            return " ".join([format_cell(key, row[key]) for key in row.keys()])

        lines = [format_row(row) for row in rows]

        return "\n".join(lines)


class CsvFormatter(TableFormatter):
    def to_string(self, rows) -> str:
        def csv_column(name: str) -> str:
            return name.capitalize().replace("_", " ")

        columns = "resource user locked_at comment".split()

        memstr = io.StringIO("")
        writer = csv.DictWriter(memstr, [csv_column(column) for column in columns])
        writer.writeheader()
        for row in rows:
            writer.writerow({csv_column(column): row[column] for column in columns})

        return memstr.getvalue()


class JsonFormatter(TableFormatter):
    def to_string(self, rows) -> str:
        return json.dumps(rows_to_dicts(rows), indent=2)


def rows_to_dicts(rows) -> List[Dict]:
    return [{key: row[key] for key in row.keys()} for row in rows]
