import unittest
from modela.data.models import *
from modela.data.DataSource import *
from google.protobuf.message import Message


class Test_Modela_configurations(unittest.TestCase):
    def test_datamodel(self):
        ty = DataLocation()
        print(ty.to_message())

    def test_parent_propagation(self):
        conf = CsvFileFormat()
        dc = DataSource()

        conf.set_parent(dc._object.spec.csvfile)
        conf.ColumnDelimiter = Delimiter.CRLF
        assert dc._object.spec.csvfile.columnDelimiter == Delimiter.CRLF.value
        dc._object.spec.csvfile.commentChars = "x"
        conf.CommentChars = "#"
        newconf = CsvFileFormat()
        newconf.copy_from(dc._object.spec.csvfile)
        assert newconf.ColumnDelimiter == Delimiter.CRLF
        assert newconf.CommentChars == "#"

        # Test propagation with subclass Message types
        conf = ExcelNotebookFormat()
        conf.set_parent(dc._object.spec.excelNotebook)
        conf.SheetName = "abc"
        conf.Data.ToColumn = 3
        assert dc._object.spec.excelNotebook.sheetName == "abc"
        assert dc._object.spec.excelNotebook.data.toColumn == 3
        conf.Data = ExcelSheetArea(ToColumn=5, EntireSheet=False)
        assert dc._object.spec.excelNotebook.data.toColumn == 5
        assert dc._object.spec.excelNotebook.data.entireSheet == False

        # Test propagation with list types
        assert len(dc._object.spec.schema.columns) == 0
        conf = Schema([Column(DataType.Text, Imputation=Imputation.ReplaceWithMean, SkewThreshold=4, Enum=["1", "2"])])
        conf.set_parent(dc._object.spec.schema)
        conf.Columns[0].Imputation = Imputation.AutoImputer
        assert dc._object.spec.schema.columns[0].imputation == Imputation.AutoImputer.value
        assert len(dc._object.spec.schema.columns) == 1
        conf.Columns.append(
            Column(DataType.Text, Imputation=Imputation.ReplaceWithMean, SkewThreshold=4, Enum=["1", "2"]))
        conf.Columns[0].Enum.append("test")
        conf.Columns[1].Enum[0] = "1337"
        assert dc._object.spec.schema.columns[0].enum[2] == "test"
        assert dc._object.spec.schema.columns[1].enum[0] == "1337"
        conf.Columns[0].Enum = ["a"]
        assert dc._object.spec.schema.columns[0].enum[0] == "a"
        conf.Columns[0].Enum.insert(0, "c")
        assert dc._object.spec.schema.columns[0].enum == ["c", "a"]
        newconf = Schema([])
        newconf.copy_from(dc._object.spec.schema)
        assert len(newconf.Columns) == 2

    def test_csv_config(self):
        conf = CsvFileFormat()
        conf.ColumnDelimiter = Delimiter.Colon
        dc = DataSource()
        dc._object.spec.csvfile.commentChars = "x"
        conf.apply_config(dc._object.spec.csvfile)
        newconf = CsvFileFormat()
        newconf.copy_from(dc._object.spec.csvfile)
        assert newconf.ColumnDelimiter == Delimiter.Colon
        assert newconf.CommentChars == "#"

    def test_excel_config(self):
        conf = ExcelNotebookFormat()
        conf.SheetName = "test"
        conf.Data.ToColumn = 3
        dc = DataSource()
        dc._object.spec.excelNotebook.data.fromColumn = 8
        conf.apply_config(dc._object.spec.excelNotebook)
        newconf = ExcelNotebookFormat()
        newconf.copy_from(dc._object.spec.excelNotebook)
        assert newconf.SheetName == "test"
        assert newconf.Data.ToColumn == 3
        assert newconf.Data.FromColumn == 1

    def test_schema_config(self):
        conf = Schema([Column(DataType.Text, Imputation=Imputation.ReplaceWithMean, SkewThreshold=4, Enum=["1", "2"]),
                       Column(DataType.Text, Imputation=Imputation.ReplaceWithMean, SkewThreshold=4, Enum=["1", "2"])])
        dc = DataSource()
        conf.apply_config(dc._object.spec.schema)
        newconf = Schema([])
        newconf.copy_from(dc._object.spec.schema)
        assert len(newconf.Columns) == 2


if __name__ == '__main__':
    unittest.main()
