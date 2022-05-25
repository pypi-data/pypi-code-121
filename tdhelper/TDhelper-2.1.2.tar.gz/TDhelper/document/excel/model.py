from .meta.modelMeta import modelMeta

class model(metaclass=modelMeta):
    __excelHandle__ = None  # excel object.
    __sheetHandle__ = None  # sheet object.
    __rows__ = []  # all rows.

    def __init__(self, excelPath, headrow=True):
        assert excelPath, "parameter <excelPath> is None."
        self.Meta.file = excelPath
        self.Meta.headrow = headrow
        try:
            self.__initExcelHandle__()
        except Exception as e:
            raise e

    def __initExcelHandle__(self):
        return None

    class Meta:
        """
        元数据
        - file: <string>, 文件路径.
        - sheet: <string>, sheet名称.
        - extension: <string>, 文件类型(xlsx,csv)
        """

        file = ""
        sheet = "sheet1"
        extension = "xlsx"
        headrow = True
