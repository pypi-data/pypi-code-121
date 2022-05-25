from TDhelper.generic.transformationType import transformation
from TDhelper.document.excel.FieldType import *
from openpyxl import load_workbook
import csv


class _AttributeOverride:
    def __init__(self, name, m_type):
        self._name = name
        self._type = m_type

    def __get__(self, instance, owen):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        instance.__dict__[self._name] = transformation(value, self._type)

    def __delete__(self, instance):
        instance.__dict__.pop(self._name)


class Meta:
    file = None
    sheet = "sheet1"
    extension = "xlsx"
    headrow = True

class modelMeta(type):
    def __new__(cls, name, bases, dct):
        attrs = {
            "mapping": {},
            "__reverse_mapping__": {},
            "__enter__": __enter__,
            "__exit__": __exit__,
            "__rows__": [],
            "close": close,
            "__initExcelHandle__": __initExcelHandle__,
            "getCount": getCount,
            "_translateMode": _translateMode,
            "__rowsCount__": 0,
            "items": items,
            "getitem": getItem,
        }
        for name, value in dct.items():
            if isinstance(dct[name], FieldType):
                attrs["mapping"][name] = value.bindCol
                attrs["__reverse_mapping__"][str(value.bindCol)] = name
                attrs[name] = _AttributeOverride(name, value.fieldType)
            else:
                attrs[name] = value
        return super(modelMeta, cls).__new__(cls, name, bases, attrs)


def __initExcelHandle__(self):
    try:
        if self.Meta.file:
            m_extension = self.Meta.file.rsplit(".")[1]
            if m_extension == "csv":
                self.Meta.extension = "csv"
                self.__excelHandle__ = open(self.Meta.file)
                self.__sheetHandle__ = csv.reader(self.__excelHandle__)
            elif m_extension == "xlsx" or m_extension == "xls":
                self.Meta.extension = "xlsx"
                self.__excelHandle__ = load_workbook(self.Meta.file)
                self.__sheetHandle__ = self.__excelHandle__[self.Meta.sheet]
            else:
                raise Exception("file extension is error.")
            if self.__sheetHandle__:
                for col in self.__sheetHandle__:
                    self.__rows__.append(col)
                if self.Meta.headrow:
                    self.__rows__.pop(0)
                self.__rowsCount__ = len(self.__rows__)
        else:
            raise Exception("meta file is None.")
    except Exception as e:
        raise e


def _translateMode(self, data=[]):
    if data:
        try:
            tmp_index = 1
            for v in data:
                if v == None or v == "None":
                    v = "0"
                setattr(
                    self,
                    self.__reverse_mapping__[str(tmp_index)],
                    v if not hasattr(v, "value") else v.value,
                )
                tmp_index += 1
            return self
        except Exception as e:
            raise e
    else:
        raise Exception("translate data is none.")


def items(self):
    assert self.Meta.file, "Meta file is none."
    for col in self.__rows__:
        result = self._translateMode(col)
        yield result


def getItem(self, offset):
    assert 0 <= offset < self.__rowsCount__, "offset %d, " % offset
    return self._translateMode(self.__rows__[offset])

def __enter__(self):
    return self

def __exit__(self, exc_type, exc_value, exc_t):
    self.close()


def close(self):
    self.__excelHandle__.close()
    if self.Meta.extension.lower() != "csv":
        self.__sheetHandle__.close()
    self.__excelHandle__ = None
    self.__sheetHandle__ = None
    self.Meta = None


def getCount(self):
    return self.__rowsCount__
